// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title BaseFlowRouter
 * @notice Trade Router for BaseFlow - routes trades with on-chain attribution
 * @dev All trades emit BotTradeExecuted events for volume tracking
 */
contract BaseFlowRouter is Ownable, ReentrancyGuard, Pausable {
    using SafeERC20 for IERC20;

    // ============ Events ============
    
    /// @notice Emitted when a trade is executed through the router
    event BotTradeExecuted(
        address indexed user,
        address indexed tokenIn,
        address indexed tokenOut,
        uint256 amountIn,
        uint256 amountOut,
        string source,
        uint256 timestamp
    );

    /// @notice Emitted when fees are collected
    event FeesCollected(
        address indexed token,
        uint256 amount,
        address indexed collector
    );

    /// @notice Emitted when a DEX router is updated
    event DexRouterUpdated(address indexed oldRouter, address indexed newRouter);

    // ============ State Variables ============

    /// @notice Fee in basis points (100 = 1%)
    uint256 public feeBps = 50; // 0.5% default fee
    
    /// @notice Maximum fee (7%)
    uint256 public constant MAX_FEE_BPS = 700;
    
    /// @notice Fee collector address
    address public feeCollector;
    
    /// @notice Uniswap V3 SwapRouter on Base
    address public uniswapRouter;
    
    /// @notice Aerodrome Router on Base
    address public aerodromeRouter;
    
    /// @notice WETH on Base
    address public constant WETH = 0x4200000000000000000000000000000000000006;
    
    /// @notice USDC on Base (excluded from volume tracking)
    address public constant USDC = 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913;
    
    /// @notice cbETH on Base (excluded from volume tracking)
    address public constant CBETH = 0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22;
    
    /// @notice Total volume tracked (in ETH value)
    uint256 public totalVolumeTracked;
    
    /// @notice Volume per token
    mapping(address => uint256) public tokenVolume;
    
    /// @notice Excluded tokens from volume tracking
    mapping(address => bool) public excludedTokens;
    
    /// @notice User trade count
    mapping(address => uint256) public userTradeCount;

    // ============ Constructor ============

    constructor(
        address _uniswapRouter,
        address _aerodromeRouter,
        address _feeCollector
    ) Ownable(msg.sender) {
        uniswapRouter = _uniswapRouter;
        aerodromeRouter = _aerodromeRouter;
        feeCollector = _feeCollector;
        
        // Exclude stablecoins and wrapped ETH variants
        excludedTokens[USDC] = true;
        excludedTokens[CBETH] = true;
    }

    // ============ External Functions ============

    /**
     * @notice Swap ETH for tokens via Uniswap V3
     * @param tokenOut The token to receive
     * @param amountOutMin Minimum tokens to receive
     * @param deadline Transaction deadline
     */
    function swapETHForTokens(
        address tokenOut,
        uint256 amountOutMin,
        uint256 deadline
    ) external payable nonReentrant whenNotPaused returns (uint256 amountOut) {
        require(msg.value > 0, "No ETH sent");
        require(deadline >= block.timestamp, "Deadline expired");
        
        // Calculate fee
        uint256 fee = (msg.value * feeBps) / 10000;
        uint256 amountIn = msg.value - fee;
        
        // Send fee to collector
        if (fee > 0 && feeCollector != address(0)) {
            (bool feeSuccess, ) = feeCollector.call{value: fee}("");
            require(feeSuccess, "Fee transfer failed");
        }
        
        // Execute swap via Uniswap V3
        // Note: This is a simplified version - production would use proper V3 params
        amountOut = _executeUniswapV3Swap(
            WETH,
            tokenOut,
            amountIn,
            amountOutMin,
            msg.sender,
            deadline
        );
        
        // Track volume if token is not excluded
        if (!excludedTokens[tokenOut]) {
            _trackVolume(msg.sender, WETH, tokenOut, amountIn, amountOut);
        }
        
        return amountOut;
    }

    /**
     * @notice Swap tokens for ETH via Uniswap V3
     * @param tokenIn The token to sell
     * @param amountIn Amount of tokens to sell
     * @param amountOutMin Minimum ETH to receive
     * @param deadline Transaction deadline
     */
    function swapTokensForETH(
        address tokenIn,
        uint256 amountIn,
        uint256 amountOutMin,
        uint256 deadline
    ) external nonReentrant whenNotPaused returns (uint256 amountOut) {
        require(amountIn > 0, "No tokens");
        require(deadline >= block.timestamp, "Deadline expired");
        
        // Transfer tokens from user
        IERC20(tokenIn).safeTransferFrom(msg.sender, address(this), amountIn);
        
        // Approve router
        IERC20(tokenIn).approve(uniswapRouter, amountIn);
        
        // Execute swap
        amountOut = _executeUniswapV3Swap(
            tokenIn,
            WETH,
            amountIn,
            amountOutMin,
            address(this),
            deadline
        );
        
        // Calculate and send fee
        uint256 fee = (amountOut * feeBps) / 10000;
        uint256 userAmount = amountOut - fee;
        
        if (fee > 0 && feeCollector != address(0)) {
            (bool feeSuccess, ) = feeCollector.call{value: fee}("");
            require(feeSuccess, "Fee transfer failed");
        }
        
        // Send ETH to user
        (bool success, ) = msg.sender.call{value: userAmount}("");
        require(success, "ETH transfer failed");
        
        // Track volume
        if (!excludedTokens[tokenIn]) {
            _trackVolume(msg.sender, tokenIn, WETH, amountIn, userAmount);
        }
        
        return userAmount;
    }

    /**
     * @notice Swap tokens for tokens via Uniswap V3
     */
    function swapTokensForTokens(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOutMin,
        uint256 deadline
    ) external nonReentrant whenNotPaused returns (uint256 amountOut) {
        require(amountIn > 0, "No tokens");
        require(deadline >= block.timestamp, "Deadline expired");
        
        // Transfer tokens from user
        IERC20(tokenIn).safeTransferFrom(msg.sender, address(this), amountIn);
        
        // Calculate fee (taken from input)
        uint256 fee = (amountIn * feeBps) / 10000;
        uint256 swapAmount = amountIn - fee;
        
        // Send fee tokens to collector
        if (fee > 0 && feeCollector != address(0)) {
            IERC20(tokenIn).safeTransfer(feeCollector, fee);
        }
        
        // Approve and execute swap
        IERC20(tokenIn).approve(uniswapRouter, swapAmount);
        amountOut = _executeUniswapV3Swap(
            tokenIn,
            tokenOut,
            swapAmount,
            amountOutMin,
            msg.sender,
            deadline
        );
        
        // Track volume for launchpad tokens only
        if (!excludedTokens[tokenIn] && !excludedTokens[tokenOut]) {
            _trackVolume(msg.sender, tokenIn, tokenOut, swapAmount, amountOut);
        }
        
        return amountOut;
    }

    // ============ Internal Functions ============

    function _executeUniswapV3Swap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOutMin,
        address recipient,
        uint256 deadline
    ) internal returns (uint256 amountOut) {
        // Uniswap V3 exactInputSingle params
        // This is a placeholder - actual implementation would use ISwapRouter interface
        
        // For now, return placeholder
        // In production: Use ISwapRouter(uniswapRouter).exactInputSingle(params)
        amountOut = amountOutMin; // Placeholder
        
        return amountOut;
    }

    function _trackVolume(
        address user,
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOut
    ) internal {
        // Update counters
        userTradeCount[user]++;
        tokenVolume[tokenIn] += amountIn;
        tokenVolume[tokenOut] += amountOut;
        totalVolumeTracked += amountIn;
        
        // Emit attribution event
        emit BotTradeExecuted(
            user,
            tokenIn,
            tokenOut,
            amountIn,
            amountOut,
            "BaseFlow",
            block.timestamp
        );
    }

    // ============ Admin Functions ============

    function setFeeBps(uint256 _feeBps) external onlyOwner {
        require(_feeBps <= MAX_FEE_BPS, "Fee too high");
        feeBps = _feeBps;
    }

    function setFeeCollector(address _feeCollector) external onlyOwner {
        feeCollector = _feeCollector;
    }

    function setUniswapRouter(address _router) external onlyOwner {
        address old = uniswapRouter;
        uniswapRouter = _router;
        emit DexRouterUpdated(old, _router);
    }

    function setAerodromeRouter(address _router) external onlyOwner {
        address old = aerodromeRouter;
        aerodromeRouter = _router;
        emit DexRouterUpdated(old, _router);
    }

    function setExcludedToken(address token, bool excluded) external onlyOwner {
        excludedTokens[token] = excluded;
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    /// @notice Emergency withdraw for stuck tokens
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        if (token == address(0)) {
            (bool success, ) = owner().call{value: amount}("");
            require(success, "ETH transfer failed");
        } else {
            IERC20(token).safeTransfer(owner(), amount);
        }
    }

    // ============ View Functions ============

    function getUserStats(address user) external view returns (
        uint256 tradeCount,
        uint256 volumeTracked
    ) {
        return (userTradeCount[user], tokenVolume[user]);
    }

    function getTokenVolume(address token) external view returns (uint256) {
        return tokenVolume[token];
    }

    // ============ Receive ============

    receive() external payable {}
}

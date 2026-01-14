import robotHero from '../assets/robot-hero.png';

export default function Hero() {
  return (
    <section id="home" className="relative bg-[#0a0e17] pt-28 pb-20 overflow-hidden grid-pattern">
      {/* Animated gradient orbs in background */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-cyan-500/20 rounded-full blur-[100px] animate-pulse"></div>
      <div className="absolute top-40 right-20 w-96 h-96 bg-purple-500/20 rounded-full blur-[120px] animate-pulse" style={{ animationDelay: '1s' }}></div>
      <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-blue-500/20 rounded-full blur-[80px] animate-pulse" style={{ animationDelay: '2s' }}></div>

      {/* Left diagonal accent */}
      <div className="absolute top-0 left-0 h-full w-1/4 pointer-events-none opacity-60">
        <svg viewBox="0 0 400 800" fill="none" xmlns="http://www.w3.org/2000/svg" className="h-full w-auto" preserveAspectRatio="none">
          <polygon points="0,0 150,0 0,600" fill="url(#grad1)" />
          <defs>
            <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#00d4ff" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#0a0e17" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      {/* Right diagonal accent */}
      <div className="absolute top-0 right-0 h-full w-1/4 pointer-events-none opacity-60">
        <svg viewBox="0 0 400 800" fill="none" xmlns="http://www.w3.org/2000/svg" className="h-full w-auto ml-auto" preserveAspectRatio="none">
          <polygon points="400,0 250,0 400,600" fill="url(#grad2)" />
          <defs>
            <linearGradient id="grad2" x1="100%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#a855f7" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#0a0e17" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      <div className="max-w-7xl mx-auto px-6 text-center relative z-10">
        <h1 className="font-crypto text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight">
          <span className="gradient-text">Trade Smarter on Base</span>
          <br />
          <span className="text-white">with AI Precision</span>
        </h1>

        <p className="text-gray-400 max-w-2xl mx-auto mb-10 text-sm md:text-base leading-relaxed">
          DEBASE Trading Bot is an AI-powered Telegram bot that automates crypto trading on the Base
          network, delivering real-time insights, optimized execution, and seamless DeFi integration.
        </p>

        <button className="relative group bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-10 py-4 rounded-xl font-semibold text-lg transition-all duration-300 hover:shadow-[0_0_30px_rgba(0,212,255,0.5)] hover:scale-105 mb-12">
          <span className="relative z-10">Launch Bot</span>
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-purple-500 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        </button>

        {/* Robot with floating coins */}
        <div className="relative max-w-lg mx-auto">
          {/* Glowing ring behind robot */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-80 h-80 rounded-full border border-cyan-500/30 animate-pulse"></div>
            <div className="absolute w-64 h-64 rounded-full border border-purple-500/20"></div>
          </div>

          {/* Left Bitcoin */}
          <div className="absolute -left-8 md:-left-20 top-1/4 z-20" style={{ animation: 'float 3s ease-in-out infinite' }}>
            <div className="w-16 h-16 md:w-20 md:h-20 rounded-full bg-gradient-to-br from-yellow-400 via-yellow-500 to-orange-500 shadow-[0_0_30px_rgba(234,179,8,0.5)] flex items-center justify-center border-2 border-yellow-300/50">
              <span className="text-2xl md:text-3xl font-bold text-yellow-900">₿</span>
            </div>
          </div>

          {/* Right Bitcoin */}
          <div className="absolute -right-8 md:-right-20 top-1/4 z-20" style={{ animation: 'float 3s ease-in-out infinite', animationDelay: '1s' }}>
            <div className="w-16 h-16 md:w-20 md:h-20 rounded-full bg-gradient-to-br from-yellow-400 via-yellow-500 to-orange-500 shadow-[0_0_30px_rgba(234,179,8,0.5)] flex items-center justify-center border-2 border-yellow-300/50">
              <span className="text-2xl md:text-3xl font-bold text-yellow-900">₿</span>
            </div>
          </div>

          {/* Small Ethereum */}
          <div className="absolute right-4 bottom-10 z-20" style={{ animation: 'float 4s ease-in-out infinite', animationDelay: '0.5s' }}>
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 shadow-[0_0_20px_rgba(168,85,247,0.5)] flex items-center justify-center border-2 border-purple-300/50">
              <span className="text-lg font-bold text-white">Ξ</span>
            </div>
          </div>

          {/* Robot Image */}
          <div className="relative z-10">
            <img
              src={robotHero}
              alt="DEBASE Trading Bot"
              className="w-full max-w-md mx-auto drop-shadow-[0_0_30px_rgba(0,212,255,0.3)]"
            />
          </div>
        </div>
      </div>

      {/* Bottom wave transition */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 100" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" className="w-full h-16 md:h-24">
          <path d="M0,100 L0,50 Q360,100 720,50 Q1080,0 1440,50 L1440,100 Z" fill="#111827" />
        </svg>
      </div>
    </section>
  );
}

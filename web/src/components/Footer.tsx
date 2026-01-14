import logo from '../assets/logo.png';

export default function Footer() {
  return (
    <footer className="bg-[#0a0e17] py-12 border-t border-gray-800">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 md:gap-12">
          {/* Logo Section */}
          <div className="col-span-2 md:col-span-1">
            <img src={logo} alt="DEBASE Trading Bot" className="h-10 mb-4" />
            <p className="text-gray-500 text-sm">
              AI-powered trading on Base
            </p>
          </div>

          {/* Product Links */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-sm font-crypto">Product</h3>
            <ul className="space-y-2">
              <li>
                <a href="#features" className="text-gray-400 hover:text-cyan-400 transition-colors text-sm">
                  Features
                </a>
              </li>
              <li>
                <a href="#docs" className="text-gray-400 hover:text-cyan-400 transition-colors text-sm">
                  Documentation
                </a>
              </li>
              <li>
                <a href="#api" className="text-gray-400 hover:text-cyan-400 transition-colors text-sm">
                  API
                </a>
              </li>
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-sm font-crypto">Company</h3>
            <ul className="space-y-2">
              <li>
                <a href="#about" className="text-gray-400 hover:text-cyan-400 transition-colors text-sm">
                  About
                </a>
              </li>
              <li>
                <a href="#blog" className="text-gray-400 hover:text-cyan-400 transition-colors text-sm">
                  Blog
                </a>
              </li>
              <li>
                <a href="#careers" className="text-gray-400 hover:text-cyan-400 transition-colors text-sm">
                  Careers
                </a>
              </li>
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-sm font-crypto">Legal</h3>
            <ul className="space-y-2">
              <li>
                <a href="#privacy" className="text-gray-400 hover:text-cyan-400 transition-colors text-sm">
                  Privacy
                </a>
              </li>
              <li>
                <a href="#terms" className="text-gray-400 hover:text-cyan-400 transition-colors text-sm">
                  Terms
                </a>
              </li>
              <li>
                <a href="#cookies" className="text-gray-400 hover:text-cyan-400 transition-colors text-sm">
                  Cookies
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-8 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-500 text-sm">
            © 2024 DEBASE Trading Bot. All rights reserved.
          </p>
          <div className="flex items-center space-x-4 mt-4 md:mt-0">
            <span className="text-gray-500 text-xs">Built on</span>
            <span className="text-cyan-400 font-crypto text-sm">Base Network</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

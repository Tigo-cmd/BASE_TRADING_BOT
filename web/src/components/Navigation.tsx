import { useState } from 'react';
import { Menu, X } from 'lucide-react';
import logo from '../assets/logo.png';

export default function Navigation() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <nav className="fixed top-0 w-full bg-[#0a0e17]/90 backdrop-blur-xl z-50 border-b border-cyan-500/10">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center">
            <img src={logo} alt="DEBASE Trading Bot" className="h-10 md:h-12" />
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <a href="#home" className="text-gray-300 hover:text-cyan-400 transition-all duration-300 font-medium relative group">
              Home
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-cyan-400 to-purple-500 group-hover:w-full transition-all duration-300"></span>
            </a>
            <a href="#about" className="text-gray-300 hover:text-cyan-400 transition-all duration-300 font-medium relative group">
              About
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-cyan-400 to-purple-500 group-hover:w-full transition-all duration-300"></span>
            </a>
            <a href="#docs" className="text-gray-300 hover:text-cyan-400 transition-all duration-300 font-medium relative group">
              Docs
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-cyan-400 to-purple-500 group-hover:w-full transition-all duration-300"></span>
            </a>
            <a href="#contact" className="text-gray-300 hover:text-cyan-400 transition-all duration-300 font-medium relative group">
              Contact Us
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-cyan-400 to-purple-500 group-hover:w-full transition-all duration-300"></span>
            </a>
          </div>

          {/* Get Started Button */}
          <a
            href="https://t.me/de_base_bot"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden md:block relative group"
          >
            <span className="relative z-10 bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-6 py-2.5 rounded-lg font-semibold block hover:shadow-[0_0_20px_rgba(0,212,255,0.4)] transition-all duration-300">
              Get Started
            </span>
          </a>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-cyan-400 p-2"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t border-cyan-500/20 pt-4">
            <div className="flex flex-col space-y-4">
              <a href="#home" className="text-gray-300 hover:text-cyan-400 transition-colors font-medium">Home</a>
              <a href="#about" className="text-gray-300 hover:text-cyan-400 transition-colors font-medium">About</a>
              <a href="#docs" className="text-gray-300 hover:text-cyan-400 transition-colors font-medium">Docs</a>
              <a href="#contact" className="text-gray-300 hover:text-cyan-400 transition-colors font-medium">Contact Us</a>
              <a
                href="https://t.me/de_base_bot"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-6 py-2.5 rounded-lg font-semibold w-fit inline-block"
              >
                Get Started
              </a>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}

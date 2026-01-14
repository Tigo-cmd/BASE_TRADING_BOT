import { Github } from 'lucide-react';

export default function Contact() {
  return (
    <section id="contact" className="bg-[#111827] py-20 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cyan-500/10 rounded-full blur-[100px]"></div>

      <div className="max-w-7xl mx-auto px-6 text-center relative z-10">
        <h2 className="font-crypto text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
          <span className="gradient-text">Contact Us</span>
        </h2>
        <p className="text-gray-400 mb-10">Get in touch with us through any of these channels</p>

        <div className="flex items-center justify-center space-x-6 md:space-x-8">
          {/* Gmail */}
          <a
            href="mailto:contact@debase.bot"
            className="group w-16 h-16 md:w-20 md:h-20 bg-gradient-to-br from-[#1a1f2e] to-[#0a0e17] rounded-2xl flex items-center justify-center border border-gray-700 hover:border-red-500/50 transition-all duration-300 hover:shadow-[0_0_30px_rgba(239,68,68,0.3)] hover:-translate-y-2"
          >
            <svg viewBox="0 0 24 24" className="w-8 h-8 md:w-10 md:h-10 group-hover:scale-110 transition-transform duration-300">
              <path fill="#EA4335" d="M24 5.457v13.909c0 .904-.732 1.636-1.636 1.636h-3.819V11.73L12 16.64l-6.545-4.91v9.273H1.636A1.636 1.636 0 0 1 0 19.366V5.457c0-2.023 2.309-3.178 3.927-1.964L5.455 4.64 12 9.548l6.545-4.91 1.528-1.145C21.69 2.28 24 3.434 24 5.457z" />
            </svg>
          </a>

          {/* X (Twitter) */}
          <a
            href="https://twitter.com/debase"
            target="_blank"
            rel="noopener noreferrer"
            className="group w-16 h-16 md:w-20 md:h-20 bg-gradient-to-br from-[#1a1f2e] to-[#0a0e17] rounded-2xl flex items-center justify-center border border-gray-700 hover:border-gray-400 transition-all duration-300 hover:shadow-[0_0_30px_rgba(255,255,255,0.2)] hover:-translate-y-2"
          >
            <svg className="w-8 h-8 md:w-10 md:h-10 text-white group-hover:scale-110 transition-transform duration-300" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
            </svg>
          </a>

          {/* GitHub */}
          <a
            href="https://github.com/debase"
            target="_blank"
            rel="noopener noreferrer"
            className="group w-16 h-16 md:w-20 md:h-20 bg-gradient-to-br from-[#1a1f2e] to-[#0a0e17] rounded-2xl flex items-center justify-center border border-gray-700 hover:border-purple-500/50 transition-all duration-300 hover:shadow-[0_0_30px_rgba(168,85,247,0.3)] hover:-translate-y-2"
          >
            <Github className="w-8 h-8 md:w-10 md:h-10 text-white group-hover:scale-110 transition-transform duration-300" strokeWidth={1.5} />
          </a>

          {/* Telegram */}
          <a
            href="https://t.me/debase"
            target="_blank"
            rel="noopener noreferrer"
            className="group w-16 h-16 md:w-20 md:h-20 bg-gradient-to-br from-[#1a1f2e] to-[#0a0e17] rounded-2xl flex items-center justify-center border border-gray-700 hover:border-cyan-500/50 transition-all duration-300 hover:shadow-[0_0_30px_rgba(0,212,255,0.3)] hover:-translate-y-2"
          >
            <svg className="w-8 h-8 md:w-10 md:h-10 text-cyan-400 group-hover:scale-110 transition-transform duration-300" viewBox="0 0 24 24" fill="currentColor">
              <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
            </svg>
          </a>
        </div>
      </div>
    </section>
  );
}

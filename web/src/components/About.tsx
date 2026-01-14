import robotPeaking from '../assets/robot-peaking.png';

export default function About() {
  return (
    <section id="about" className="bg-[#111827] py-20 md:py-28 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-[100px]"></div>
      <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-purple-500/10 rounded-full blur-[80px]"></div>

      <div className="max-w-7xl mx-auto px-6 relative z-10">
        <h2 className="font-crypto text-3xl md:text-4xl lg:text-5xl font-bold text-center mb-16">
          <span className="text-white">Why </span>
          <span className="gradient-text">Debase Trading Bot</span>
          <span className="text-white"> ?</span>
        </h2>

        <div className="flex flex-col md:flex-row items-center gap-12 md:gap-16">
          {/* Robot Image */}
          <div className="flex-1 flex justify-center md:justify-end">
            <div className="relative group">
              {/* Glow effect behind image */}
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/20 to-purple-500/20 rounded-full blur-3xl group-hover:blur-2xl transition-all duration-500"></div>
              <img
                src={robotPeaking}
                alt="DEBASE Trading Bot Robot"
                className="relative z-10 w-64 md:w-80 lg:w-96 drop-shadow-[0_0_30px_rgba(0,212,255,0.2)] hover:scale-105 transition-transform duration-500"
              />
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 space-y-6">
            <div className="crypto-card p-8 rounded-2xl">
              <p className="text-gray-300 text-base md:text-lg leading-relaxed">
                <span className="font-bold text-cyan-400 tracking-wider font-crypto">DEBASE TRADING BOT</span> is an AI-powered Telegram
                trading bot tailored for the Base network, designed to automate and optimize cryptocurrency trading
                within the Ethereum Layer 2 ecosystem. Leveraging advanced algorithms, real-time market analysis, and
                seamless integration with Base's DeFi protocols, our bot empowers users to execute trades efficiently,
                manage portfolios, and capitalize on AI-driven strategies for tokens on the Base chain.
              </p>
            </div>

            <a
              href="https://t.me/de_base_bot"
              target="_blank"
              rel="noopener noreferrer"
              className="relative group inline-block bg-gradient-to-r from-cyan-500 to-purple-600 text-white px-8 py-3.5 rounded-xl font-semibold transition-all duration-300 hover:shadow-[0_0_25px_rgba(0,212,255,0.4)] hover:scale-105"
            >
              Start Trading
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

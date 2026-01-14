import { RefreshCw, Shield, TrendingUp, Briefcase, Bell, Users } from 'lucide-react';

const features = [
  {
    icon: RefreshCw,
    title: 'Automated Trading',
    description: 'Execute Trades Using Predefined Strategies Tailored To Base Tokens.',
    color: 'from-cyan-500 to-blue-600',
  },
  {
    icon: Shield,
    title: 'Risk Management',
    description: 'Custom Stop-Loss And Take-Profit Controls.',
    color: 'from-purple-500 to-pink-600',
  },
  {
    icon: TrendingUp,
    title: 'Smart Market Analysis',
    description: "AI-Driven Analysis For Detecting Trends In Base's DeFi Markets.",
    color: 'from-green-500 to-emerald-600',
  },
  {
    icon: Briefcase,
    title: 'Portfolio Management',
    description: 'Automated Diversification And Rebalancing.',
    color: 'from-orange-500 to-red-600',
  },
  {
    icon: Bell,
    title: 'Real-Time Alerts',
    description: 'Instant Notifications For Trades, Prices, And Network Events.',
    color: 'from-blue-500 to-indigo-600',
  },
  {
    icon: Users,
    title: 'Copy Trading & Signals',
    description: 'Follow Top Base Traders And Premium Signal Providers.',
    color: 'from-pink-500 to-purple-600',
  },
];

export default function Features() {
  return (
    <section className="bg-[#0a0e17] py-20 md:py-28 relative overflow-hidden grid-pattern">
      {/* Background glows */}
      <div className="absolute top-20 left-20 w-80 h-80 bg-cyan-500/10 rounded-full blur-[100px]"></div>
      <div className="absolute bottom-20 right-20 w-80 h-80 bg-purple-500/10 rounded-full blur-[100px]"></div>

      <div className="max-w-6xl mx-auto px-6 relative z-10">
        <h2 className="font-crypto text-3xl md:text-4xl lg:text-5xl font-bold text-center mb-4">
          <span className="text-white">What can </span>
          <span className="gradient-text">Debase trading</span>
          <span className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-xl text-2xl mx-2 shadow-[0_0_20px_rgba(0,212,255,0.4)]">🤖</span>
          <span className="text-white">do ?</span>
        </h2>

        <p className="text-gray-400 text-center max-w-2xl mx-auto mb-12">
          Powerful features designed to maximize your trading potential on the Base network
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="group relative bg-gradient-to-br from-[#111827] to-[#0a0e17] rounded-2xl p-6 border border-gray-800 hover:border-cyan-500/50 transition-all duration-500 hover:shadow-[0_0_30px_rgba(0,212,255,0.15)] hover:-translate-y-2"
            >
              {/* Gradient corner accent */}
              <div className={`absolute top-0 right-0 w-20 h-20 bg-gradient-to-br ${feature.color} opacity-10 rounded-bl-[80px] rounded-tr-2xl`}></div>

              <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 shadow-lg group-hover:shadow-[0_0_20px_rgba(0,212,255,0.3)] transition-shadow duration-300`}>
                <feature.icon className="w-7 h-7 text-white" strokeWidth={2} />
              </div>

              <h3 className="text-lg font-bold text-white mb-2 group-hover:text-cyan-400 transition-colors duration-300">{feature.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

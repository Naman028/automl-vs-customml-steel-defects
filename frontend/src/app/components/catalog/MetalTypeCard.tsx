import React from "react";
import { MetalType } from "../../services/api";

type MetalTypeCardProps = {
  metal: MetalType;
  index: number;
};

export const MetalTypeCard: React.FC<MetalTypeCardProps> = ({
  metal,
  index,
}) => {
  return (
    <div
      key={metal.name}
      className="flex-shrink-0 w-80 snap-center group"
      style={{
        animation: `fadeInUp 0.6s ease-out ${index * 0.1}s both`,
      }}
    >
      <div className="relative h-full bg-gradient-to-br from-white to-slate-50 dark:from-slate-800 dark:to-slate-900 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 transition-all duration-500 hover:shadow-2xl hover:shadow-slate-900/10 dark:hover:shadow-slate-950/50 hover:-translate-y-2">
        <div className="relative h-56 overflow-hidden bg-slate-100 dark:bg-slate-950">
          <img
            src={metal.imageUrl}
            alt={metal.displayName}
            className="w-full h-full object-cover transition-all duration-700 group-hover:scale-110 group-hover:brightness-110"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-60 group-hover:opacity-40 transition-opacity duration-500"></div>

          <div className="absolute top-4 right-4">
            <div
              className={`px-3 py-1.5 rounded-lg bg-gradient-to-r ${metal.color} backdrop-blur-md border border-white/20 shadow-lg`}
            >
              <span className="text-white text-xs tracking-wider">
                CERTIFIED
              </span>
            </div>
          </div>
        </div>

        <div className="p-6">
          <h3 className="text-xl text-slate-900 dark:text-white mb-2 tracking-tight group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-slate-700 group-hover:to-slate-900 dark:group-hover:from-slate-300 dark:group-hover:to-white transition-all duration-300">
            {metal.displayName}
          </h3>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-4 leading-relaxed">
            {metal.description}
          </p>

          <div className="flex items-center gap-3 pt-4 border-t border-slate-200 dark:border-slate-700">
            <div
              className={`w-1.5 h-1.5 rounded-full bg-gradient-to-r ${metal.color}`}
            ></div>
            <p className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              {metal.properties}
            </p>
          </div>
        </div>

        <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-1000 pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
        </div>
      </div>
    </div>
  );
};

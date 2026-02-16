import React from "react";
import { MetalType } from "../../services/api";
import { MetalTypeCard } from "./MetalTypeCard";

type MetalTypesCarouselProps = {
  items: MetalType[];
};

export const MetalTypesCarousel: React.FC<MetalTypesCarouselProps> = ({
  items,
}) => {
  return (
    <div className="relative">
      <div className="flex overflow-x-auto pb-6 gap-6 scrollbar-thin scrollbar-thumb-slate-300 dark:scrollbar-thumb-slate-700 snap-x snap-mandatory">
        {items.map((metal, index) => (
          <MetalTypeCard key={metal.name} metal={metal} index={index} />
        ))}
      </div>
    </div>
  );
};

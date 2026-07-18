import { MetalType, SteelDefect } from "./types";

export const BACKEND_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8001";

export const CLASS_MAP: Record<string, string> = {
  Cr: "Crazing",
  In: "Inclusion",
  Pa: "Patches",
  PS: "Pitted",
  RS: "Rolled-in Scale",
  Sc: "Scratches",
  Crazing: "Crazing",
  Inclusion: "Inclusion",
  Patches: "Patches",
  Pitted: "Pitted",
  Pitted_Surface: "Pitted",
  "Pitted Surface": "Pitted",
  Rolled_in_Scale: "Rolled-in Scale",
  "Rolled-in Scale": "Rolled-in Scale",
  "Rolled in Scale": "Rolled-in Scale",
  Scratches: "Scratches",
  "No defect / Unknown": "No Defect",
};

export const metalTypes: MetalType[] = [
  {
    name: "steel",
    displayName: "Steel",
    description: "Iron-carbon alloy",
    properties: "High strength, durable",
    imageUrl: "/metals/steel.jpg",
    color: "from-gray-600 to-gray-800",
  },
  {
    name: "aluminum",
    displayName: "Aluminum",
    description: "Lightweight metal",
    properties: "Corrosion resistant",
    imageUrl: "/metals/aluminium.jpg",
    color: "from-blue-400 to-blue-600",
  },
  {
    name: "copper",
    displayName: "Copper",
    description: "Conductive metal",
    properties: "Excellent conductivity",
    imageUrl: "/metals/copper.jpg",
    color: "from-orange-600 to-red-700",
  },
  {
    name: "titanium",
    displayName: "Titanium",
    description: "High-performance alloy",
    properties: "Strong, lightweight",
    imageUrl: "/metals/titanium.jpg",
    color: "from-purple-600 to-indigo-700",
  },
  {
    name: "brass",
    displayName: "Brass",
    description: "Copper-zinc alloy",
    properties: "Decorative, malleable",
    imageUrl: "/metals/brass.jpg",
    color: "from-yellow-600 to-amber-700",
  },
  {
    name: "stainless_steel",
    displayName: "Stainless Steel",
    description: "Corrosion-resistant steel",
    properties: "Anti-corrosive, hygienic",
    imageUrl: "/metals/Stainless_steel.jpg",
    color: "from-slate-500 to-zinc-700",
  },
  {
    name: "bronze",
    displayName: "Bronze",
    description: "Copper-tin alloy",
    properties: "Wear resistant",
    imageUrl: "/metals/bronze.jpg",
    color: "from-amber-700 to-orange-800",
  },
  {
    name: "nickel",
    displayName: "Nickel",
    description: "Corrosion-resistant",
    properties: "Heat resistant",
    imageUrl: "/metals/nickel.jpg",
    color: "from-emerald-600 to-teal-700",
  },
];

export const steelDefects: SteelDefect[] = [
  {
    name: "crazing",
    displayName: "Crazing",
    description: "Thermal cracks",
    severity: "Medium",
    imageUrl: "/defects/crazing.jpg",
  },
  {
    name: "inclusion",
    displayName: "Inclusion",
    description: "Foreign particles",
    severity: "High",
    imageUrl: "/defects/inclusion.jpg",
  },
  {
    name: "patches",
    displayName: "Patches",
    description: "Raised surfaces",
    severity: "Medium",
    imageUrl: "/defects/patches.jpg",
  },
  {
    name: "pitted",
    displayName: "Pitted",
    description: "Small holes",
    severity: "High",
    imageUrl: "/defects/pitted.jpg",
  },
  {
    name: "rolled_in_scale",
    displayName: "Rolled-in Scale",
    description: "Scale trapped",
    severity: "Medium",
    imageUrl: "/defects/rolled_in_scale.jpg",
  },
  {
    name: "scratches",
    displayName: "Scratches",
    description: "Surface marks",
    severity: "Low",
    imageUrl: "/defects/scratches.jpg",
  },
];

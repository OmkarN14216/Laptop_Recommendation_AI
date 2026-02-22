import React from 'react';
import { Laptop, DollarSign, Cpu, HardDrive, Star } from 'lucide-react';

const LaptopCard = ({ laptop, rank }) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow relative">
      {/* Rank Badge */}
      <div className="absolute top-4 right-4 bg-gradient-to-r from-yellow-400 to-orange-500 text-white w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg shadow-lg">
        #{rank}
      </div>
      
      <div className="flex items-center justify-between mb-4 pr-12">
        <div className="flex items-center">
          <Laptop className="text-blue-500 mr-2" size={24} />
          <h3 className="text-xl font-bold">{laptop.brand}</h3>
        </div>
      </div>
      
      <h4 className="text-lg font-semibold mb-3 text-gray-800">{laptop.model_name}</h4>
      
      {/* Match Score */}
      <div className="mb-4 flex items-center gap-2">
        <Star className="text-yellow-500" size={20} fill="currentColor" />
        <div className="flex-1">
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm font-medium">Match Score</span>
            <span className="text-sm font-bold text-green-600">{laptop.score}/9</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-green-400 to-green-600 h-2 rounded-full transition-all"
              style={{ width: `${(laptop.score / 9) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>
      
      <div className="space-y-2 mb-4 text-sm">
        <div className="flex items-center text-gray-600">
          <Cpu size={16} className="mr-2 flex-shrink-0" />
          <span>{laptop.cpu_manufacturer} {laptop.core} @ {laptop.clock_speed}</span>
        </div>
        <div className="flex items-center text-gray-600">
          <HardDrive size={16} className="mr-2 flex-shrink-0" />
          <span>{laptop.ram_size} RAM | {laptop.storage_type}</span>
        </div>
        <div className="text-gray-600">
          <span className="font-semibold">Display:</span> {laptop.display_size} {laptop.display_type}
        </div>
        <div className="text-gray-600">
          <span className="font-semibold">GPU:</span> {laptop.graphics_processor}
        </div>
        <div className="text-gray-600">
          <span className="font-semibold">Weight:</span> {laptop.laptop_weight}
        </div>
        <div className="text-gray-600">
          <span className="font-semibold">Battery:</span> {laptop.average_battery_life}
        </div>
      </div>
      
      <div className="border-t pt-4 mt-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center text-2xl font-bold text-blue-600">
            <DollarSign size={20} />
            <span>₹{laptop.price.toLocaleString()}</span>
          </div>
          <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors text-sm">
            View Details
          </button>
        </div>
      </div>
      
      {laptop.description && (
        <div className="mt-4 text-xs text-gray-500 border-t pt-3">
          <p className="line-clamp-2">{laptop.description}</p>
        </div>
      )}
    </div>
  );
};

export default LaptopCard;
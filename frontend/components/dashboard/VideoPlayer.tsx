import { Play } from "lucide-react";

export function VideoPlayer() {
  return (
    <div className="w-full h-full relative group">
        {/* Placeholder Gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-950 to-black opacity-100" />
        
        {/* Grid Pattern */}
            <div className="absolute inset-0 opacity-20" 
            style={{ backgroundImage: 'radial-gradient(circle, #ffffff 1px, transparent 1px)', backgroundSize: '24px 24px' }} 
        />

        {/* Play Button */}
        <div className="absolute inset-0 flex items-center justify-center cursor-pointer">
            <button className="h-16 w-16 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 flex items-center justify-center text-white transition-transform group-hover:scale-110 group-active:scale-95 shadow-2xl">
                <Play className="h-8 w-8 ml-1 fill-white" />
            </button>
        </div>

        {/* Status Overlay */}
        <div className="absolute bottom-4 left-4 right-4">
            <div className="bg-black/40 backdrop-blur-md rounded px-3 py-2 border border-white/5">
                <h3 className="text-white font-medium text-sm">Preview: Physics 101 - Gravity</h3>
                <div className="flex justify-between items-center mt-1">
                    <span className="text-[10px] text-gray-300 font-mono">00:00 / 01:20</span>
                    <span className="text-[10px] text-indigo-300 font-mono flex items-center gap-1.5">
                            <div className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-pulse"/>
                            Waiting for renderer...
                    </span>
                </div>
            </div>
        </div>
    </div>
  );
}

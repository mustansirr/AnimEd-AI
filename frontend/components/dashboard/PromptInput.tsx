import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Upload, Sparkles, Link } from "lucide-react";

export function PromptInput() {
  return (
    <Card className="h-full border shadow-sm bg-white">
      <CardContent className="p-4 space-y-4">
        {/* Header/Title Area */}
        <div className="flex items-center justify-between">
            <h3 className="font-semibold text-sm flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-500" />
                What’s today’s lesson or concept?
            </h3>
            <Button variant="ghost" size="sm" className="h-8 text-[10px] text-muted-foreground hover:text-red-500">
                Clear
            </Button>
        </div>

        {/* Text Area */}
        <Textarea 
            id="prompt"
            placeholder="Topic: Introduction to Gravity for high school students.&#10;Tone: Engaging, slightly humorous but educational.&#10;Key points to cover:&#10;1. Newton's Apple myth vs reality.&#10;..." 
            className="min-h-[120px] resize-none border-gray-100 bg-gray-50/50 focus-visible:ring-1 focus-visible:ring-indigo-500 font-mono text-sm"
        />

        {/* Action Footer */}
        <div className="flex items-center justify-between pt-2">
            <div className="flex items-center gap-2">
                 <Button variant="outline" size="sm" className="h-8 text-xs gap-2 bg-gray-50">
                    <Upload className="w-3 h-3" />
                    Upload PDF
                </Button>
                 <Button variant="outline" size="sm" className="h-8 text-xs gap-2 bg-gray-50">
                    <Link className="w-3 h-3" />
                    Add URL
                </Button>
            </div>
            
            <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm transition-all gap-2 text-xs h-8">
                Generate
            </Button>
        </div>

      </CardContent>
    </Card>
  );
}

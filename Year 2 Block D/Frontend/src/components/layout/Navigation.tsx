
import React from "react";
import { NavLink } from "react-router-dom";
import { MenuIcon, BarChart2, Video, Settings, ChevronDown, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";

const Navigation = () => {
  const [isMobileNavOpen, setIsMobileNavOpen] = React.useState(false);

  const navLinks = [
    {
      title: "Dashboard",
      path: "/",
      icon: <BarChart2 className="h-4 w-4" />,
    },
    {
      title: "Analysis",
      path: "/analysis",
      icon: <Video className="h-4 w-4" />,
      isNew: true,
    },
    {
      title: "History",
      path: "/history",
      icon: <BarChart2 className="h-4 w-4" />,
    },
    {
      title: "Settings",
      path: "/settings",
      icon: <Settings className="h-4 w-4" />,
    },
  ];

  return (
    <header className="sticky top-0 z-30 w-full bg-background/80 backdrop-blur-md border-b border-border">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center">
          <NavLink to="/" className="flex items-center gap-2 mr-8">
            <div className="h-8 w-8 bg-primary/20 border border-primary/20 rounded flex items-center justify-center text-primary font-medium">EA</div>
            <span className="font-heading text-lg">Emotion<span className="text-primary">AI</span></span>
          </NavLink>
          
          <nav className="hidden md:flex items-center space-x-1">
            {navLinks.map((link) => (
              <NavLink
                key={link.path}
                to={link.path}
                className={({ isActive }) => 
                  `flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive 
                      ? "bg-secondary text-primary" 
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                  }`
                }
              >
                <span className="flex items-center gap-2">
                  {link.icon}
                  {link.title}
                </span>
                {link.isNew && (
                  <Badge className="ml-2 bg-primary/20 text-primary text-[10px] h-5" variant="secondary">
                    New
                  </Badge>
                )}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            className="hidden md:flex bg-secondary/50 border-border hover:bg-secondary"
          >
            <span>Free Plan</span>
            <ChevronDown className="h-3 w-3 ml-1 opacity-70" />
          </Button>
          
          <Button 
            variant="ghost" 
            size="icon" 
            className="md:hidden" 
            onClick={() => setIsMobileNavOpen(!isMobileNavOpen)}
          >
            {isMobileNavOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <MenuIcon className="h-5 w-5" />
            )}
          </Button>
        </div>
      </div>
      
      {/* Mobile Navigation */}
      {isMobileNavOpen && (
        <div className="md:hidden fixed inset-0 z-40 pt-16 bg-background/95 backdrop-blur-lg animate-fade-in">
          <nav className="container py-6 flex flex-col gap-1">
            {navLinks.map((link) => (
              <NavLink
                key={link.path}
                to={link.path}
                className={({ isActive }) => 
                  `flex items-center py-3 px-4 rounded-md text-sm font-medium ${
                    isActive 
                      ? "bg-secondary text-primary" 
                      : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
                  }`
                }
                onClick={() => setIsMobileNavOpen(false)}
              >
                <span className="flex items-center gap-3">
                  {link.icon}
                  {link.title}
                </span>
                {link.isNew && (
                  <Badge className="ml-2 bg-primary/20 text-primary text-[10px]" variant="secondary">
                    New
                  </Badge>
                )}
              </NavLink>
            ))}
            <Separator className="my-4 bg-border" />
            <div className="px-4 py-3">
              <Button 
                variant="outline" 
                size="sm" 
                className="w-full justify-between"
              >
                <span>Free Plan</span>
                <ChevronDown className="h-3 w-3 opacity-70" />
              </Button>
            </div>
          </nav>
        </div>
      )}
    </header>
  );
};

export default Navigation;


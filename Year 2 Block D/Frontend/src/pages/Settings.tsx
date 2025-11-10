
import React, { useState } from "react";
import { Settings as SettingsIcon, User, Bell, Shield, Palette, Download, Upload, Trash2, Save, Moon, Sun, Monitor } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import Navigation from "@/components/layout/Navigation";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";

const Settings = () => {
  const { toast } = useToast();
  const [settings, setSettings] = useState({
    notifications: {
      email: true,
      browser: false,
      analysis: true,
      weekly: false
    },
    privacy: {
      dataCollection: true,
      analytics: false,
      marketing: false
    },
    appearance: {
      theme: "dark",
      animations: true,
      compactMode: false
    },
    profile: {
      name: "John Doe",
      email: "john@example.com",
      company: "EmotionAI"
    }
  });

  const handleSave = () => {
    toast({
      title: "Settings Saved",
      description: "Your preferences have been updated successfully."
    });
  };

  const handleExportData = () => {
    toast({
      title: "Data Export Started",
      description: "Your data export will be ready for download shortly."
    });
  };

  const handleDeleteAccount = () => {
    toast({
      variant: "destructive",
      title: "Account Deletion",
      description: "This action cannot be undone. Please contact support to proceed."
    });
  };

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground relative overflow-hidden">
      {/* Enhanced animated background */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-0 right-[20%] w-80 h-80 rounded-full bg-gradient-to-br from-primary/20 via-accent/15 to-transparent filter blur-[120px] animate-pulse-light" />
        <div className="absolute bottom-0 left-[15%] w-96 h-96 rounded-full bg-gradient-to-tr from-accent/20 via-primary/15 to-transparent filter blur-[100px] animate-float" />
      </div>
      <div className="noise-overlay opacity-20"></div>
      
      <Navigation />
      
      <main className="flex-1 container py-12 relative z-10">
        <div className="mb-12 text-center">
          <Badge className="bg-gradient-to-r from-primary/20 to-accent/20 text-primary border-primary/30 backdrop-blur-sm px-4 py-2 mb-4 animate-fade-in">
            <SettingsIcon className="w-4 h-4 mr-2" />
            Settings & Preferences
          </Badge>
          <h1 className="text-4xl md:text-6xl font-bold mb-4 text-gradient animate-slide-up">Settings</h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto animate-slide-up">
            Customize your EmotionAI experience and manage your account preferences
          </p>
        </div>

        <Tabs defaultValue="profile" className="max-w-4xl mx-auto">
          <TabsList className="grid grid-cols-2 md:grid-cols-4 w-full glass-panel border border-white/10 p-1 mb-8">
            <TabsTrigger 
              value="profile" 
              className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-primary data-[state=active]:to-accent data-[state=active]:text-white transition-all duration-300"
            >
              <User className="h-4 w-4 mr-2" />
              Profile
            </TabsTrigger>
            <TabsTrigger 
              value="notifications" 
              className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-primary data-[state=active]:to-accent data-[state=active]:text-white transition-all duration-300"
            >
              <Bell className="h-4 w-4 mr-2" />
              Notifications
            </TabsTrigger>
            <TabsTrigger 
              value="appearance" 
              className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-primary data-[state=active]:to-accent data-[state=active]:text-white transition-all duration-300"
            >
              <Palette className="h-4 w-4 mr-2" />
              Appearance
            </TabsTrigger>
            <TabsTrigger 
              value="privacy" 
              className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-primary data-[state=active]:to-accent data-[state=active]:text-white transition-all duration-300"
            >
              <Shield className="h-4 w-4 mr-2" />
              Privacy
            </TabsTrigger>
          </TabsList>

          <TabsContent value="profile" className="space-y-6 animate-slide-up">
            <Card className="glass-panel rounded-2xl border border-white/10 shadow-2xl">
              <CardHeader>
                <CardTitle className="text-2xl text-gradient flex items-center gap-3">
                  <div className="h-10 w-10 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
                    <User className="h-6 w-6 text-white" />
                  </div>
                  Profile Information
                </CardTitle>
                <CardDescription className="text-base">
                  Update your personal information and account details
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="name" className="text-base font-medium">Full Name</Label>
                    <Input 
                      id="name"
                      value={settings.profile.name}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        profile: { ...prev.profile, name: e.target.value }
                      }))}
                      className="glass-card border-white/20 focus-visible:ring-primary/50 h-12"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-base font-medium">Email Address</Label>
                    <Input 
                      id="email"
                      type="email"
                      value={settings.profile.email}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        profile: { ...prev.profile, email: e.target.value }
                      }))}
                      className="glass-card border-white/20 focus-visible:ring-primary/50 h-12"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="company" className="text-base font-medium">Company (Optional)</Label>
                  <Input 
                    id="company"
                    value={settings.profile.company}
                    onChange={(e) => setSettings(prev => ({
                      ...prev,
                      profile: { ...prev.profile, company: e.target.value }
                    }))}
                    className="glass-card border-white/20 focus-visible:ring-primary/50 h-12"
                  />
                </div>
              </CardContent>
            </Card>

            <Card className="glass-panel rounded-2xl border border-white/10 shadow-2xl">
              <CardHeader>
                <CardTitle className="text-xl text-gradient">Account Actions</CardTitle>
                <CardDescription>Manage your account data and preferences</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Button 
                    variant="outline" 
                    onClick={handleExportData}
                    className="glass-card border-white/20 hover:border-blue-500/50 hover:bg-blue-500/10 transition-all duration-300 h-12"
                  >
                    <Download className="h-5 w-5 mr-2" />
                    Export Data
                  </Button>
                  <Button 
                    variant="outline" 
                    className="glass-card border-white/20 hover:border-green-500/50 hover:bg-green-500/10 transition-all duration-300 h-12"
                  >
                    <Upload className="h-5 w-5 mr-2" />
                    Import Data
                  </Button>
                </div>
                <Separator className="bg-white/10" />
                <Button 
                  variant="destructive" 
                  onClick={handleDeleteAccount}
                  className="w-full bg-red-600/20 border border-red-600/30 text-red-400 hover:bg-red-600/30 h-12"
                >
                  <Trash2 className="h-5 w-5 mr-2" />
                  Delete Account
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="notifications" className="space-y-6 animate-slide-up">
            <Card className="glass-panel rounded-2xl border border-white/10 shadow-2xl">
              <CardHeader>
                <CardTitle className="text-2xl text-gradient flex items-center gap-3">
                  <div className="h-10 w-10 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
                    <Bell className="h-6 w-6 text-white" />
                  </div>
                  Notification Preferences
                </CardTitle>
                <CardDescription className="text-base">
                  Control how and when you receive notifications
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {[
                  { key: 'email', label: 'Email Notifications', description: 'Receive updates via email' },
                  { key: 'browser', label: 'Browser Notifications', description: 'Show notifications in your browser' },
                  { key: 'analysis', label: 'Analysis Complete', description: 'Notify when analysis is finished' },
                  { key: 'weekly', label: 'Weekly Reports', description: 'Receive weekly summary reports' }
                ].map((item) => (
                  <div key={item.key} className="flex items-center justify-between p-4 glass-card rounded-xl border border-white/10 hover:border-white/20 transition-all duration-300">
                    <div className="space-y-1">
                      <Label className="text-base font-medium">{item.label}</Label>
                      <p className="text-sm text-muted-foreground">{item.description}</p>
                    </div>
                    <Switch 
                      checked={settings.notifications[item.key as keyof typeof settings.notifications]}
                      onCheckedChange={(checked) => setSettings(prev => ({
                        ...prev,
                        notifications: { ...prev.notifications, [item.key]: checked }
                      }))}
                    />
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="appearance" className="space-y-6 animate-slide-up">
            <Card className="glass-panel rounded-2xl border border-white/10 shadow-2xl">
              <CardHeader>
                <CardTitle className="text-2xl text-gradient flex items-center gap-3">
                  <div className="h-10 w-10 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
                    <Palette className="h-6 w-6 text-white" />
                  </div>
                  Appearance Settings
                </CardTitle>
                <CardDescription className="text-base">
                  Customize the look and feel of your interface
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <Label className="text-base font-medium">Theme Preference</Label>
                  <div className="grid grid-cols-3 gap-4">
                    {[
                      { value: 'light', label: 'Light', icon: <Sun className="h-5 w-5" /> },
                      { value: 'dark', label: 'Dark', icon: <Moon className="h-5 w-5" /> },
                      { value: 'system', label: 'System', icon: <Monitor className="h-5 w-5" /> }
                    ].map((theme) => (
                      <Button
                        key={theme.value}
                        variant={settings.appearance.theme === theme.value ? "default" : "outline"}
                        onClick={() => setSettings(prev => ({
                          ...prev,
                          appearance: { ...prev.appearance, theme: theme.value }
                        }))}
                        className={`h-16 ${settings.appearance.theme === theme.value 
                          ? 'bg-gradient-to-r from-primary to-accent text-white' 
                          : 'glass-card border-white/20 hover:border-white/40'
                        } transition-all duration-300`}
                      >
                        <div className="flex flex-col items-center gap-2">
                          {theme.icon}
                          <span className="text-sm">{theme.label}</span>
                        </div>
                      </Button>
                    ))}
                  </div>
                </div>

                <Separator className="bg-white/10" />

                {[
                  { key: 'animations', label: 'Enable Animations', description: 'Show smooth transitions and effects' },
                  { key: 'compactMode', label: 'Compact Mode', description: 'Use a more compact interface layout' }
                ].map((item) => (
                  <div key={item.key} className="flex items-center justify-between p-4 glass-card rounded-xl border border-white/10 hover:border-white/20 transition-all duration-300">
                    <div className="space-y-1">
                      <Label className="text-base font-medium">{item.label}</Label>
                      <p className="text-sm text-muted-foreground">{item.description}</p>
                    </div>
                    <Switch 
                      checked={settings.appearance[item.key as keyof typeof settings.appearance] as boolean}
                      onCheckedChange={(checked) => setSettings(prev => ({
                        ...prev,
                        appearance: { ...prev.appearance, [item.key]: checked }
                      }))}
                    />
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="privacy" className="space-y-6 animate-slide-up">
            <Card className="glass-panel rounded-2xl border border-white/10 shadow-2xl">
              <CardHeader>
                <CardTitle className="text-2xl text-gradient flex items-center gap-3">
                  <div className="h-10 w-10 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
                    <Shield className="h-6 w-6 text-white" />
                  </div>
                  Privacy & Security
                </CardTitle>
                <CardDescription className="text-base">
                  Control your data privacy and security settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {[
                  { key: 'dataCollection', label: 'Anonymous Data Collection', description: 'Help improve our services with anonymous usage data' },
                  { key: 'analytics', label: 'Analytics Tracking', description: 'Allow us to track usage for analytics purposes' },
                  { key: 'marketing', label: 'Marketing Communications', description: 'Receive promotional emails and updates' }
                ].map((item) => (
                  <div key={item.key} className="flex items-center justify-between p-4 glass-card rounded-xl border border-white/10 hover:border-white/20 transition-all duration-300">
                    <div className="space-y-1">
                      <Label className="text-base font-medium">{item.label}</Label>
                      <p className="text-sm text-muted-foreground">{item.description}</p>
                    </div>
                    <Switch 
                      checked={settings.privacy[item.key as keyof typeof settings.privacy]}
                      onCheckedChange={(checked) => setSettings(prev => ({
                        ...prev,
                        privacy: { ...prev.privacy, [item.key]: checked }
                      }))}
                    />
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <div className="mt-12 flex justify-center">
          <Button 
            onClick={handleSave}
            className="bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white shadow-2xl hover:shadow-primary/25 transition-all duration-300 px-8 py-3 text-lg"
          >
            <Save className="h-5 w-5 mr-2" />
            Save All Settings
          </Button>
        </div>
      </main>
      
      <footer className="glass-panel border-t border-white/10 py-8 relative z-10">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 bg-gradient-to-br from-primary to-accent rounded-xl flex items-center justify-center text-white font-bold shadow-lg">
                EA
              </div>
              <span className="font-heading text-lg">Emotion<span className="text-gradient">AI</span></span>
            </div>
            <p className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} EmotionAI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Settings;

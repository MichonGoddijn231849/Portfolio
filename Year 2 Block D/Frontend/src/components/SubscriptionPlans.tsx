
import React from "react";
import { Check, X, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const plans = [
  {
    name: "Starter",
    price: "$0",
    period: "forever",
    description: "Basic emotion analysis for personal use",
    features: [
      { name: "5 videos per month", included: true },
      { name: "7 basic emotions", included: true },
      { name: "5-minute video limit", included: true },
      { name: "Priority support", included: false },
      { name: "API access", included: false },
      { name: "Advanced analytics", included: false },
    ],
    transcriptionModel: "tiny",
    popular: false,
    buttonText: "Current Plan",
    buttonDisabled: true,
  },
  {
    name: "Creator",
    price: "$12",
    period: "per month",
    description: "Advanced analysis for creators and professionals",
    features: [
      { name: "Unlimited videos", included: true },
      { name: "25+ emotion categories", included: true },
      { name: "30-minute video limit", included: true },
      { name: "Priority support", included: true },
      { name: "API access", included: false },
      { name: "Advanced analytics", included: true },
    ],
    transcriptionModel: "medium",
    popular: true,
    buttonText: "Upgrade",
    buttonDisabled: false,
  },
  {
    name: "Enterprise",
    price: "$49",
    period: "per month",
    description: "Complete solution for businesses and research",
    features: [
      { name: "Unlimited videos", included: true },
      { name: "30+ emotion categories", included: true },
      { name: "No video length limit", included: true },
      { name: "Priority support", included: true },
      { name: "API access", included: true },
      { name: "Advanced analytics", included: true },
    ],
    transcriptionModel: "turbo",
    popular: false,
    buttonText: "Contact Sales",
    buttonDisabled: false,
  },
];

const SubscriptionPlans = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {plans.map((plan) => (
        <Card 
          key={plan.name} 
          className={`glass-card rounded-xl relative ${
            plan.popular ? "border-primary/30 ring-1 ring-primary/20" : "border-border"
          }`}
        >
          {plan.popular && (
            <div className="absolute -top-3 -right-3">
              <Badge className="bg-primary text-white flex items-center gap-1.5 py-1 px-2.5">
                <Star className="h-3.5 w-3.5" /> Popular
              </Badge>
            </div>
          )}
          
          <CardHeader>
            <CardTitle className="flex flex-col gap-1">
              <span>{plan.name}</span>
              <div className="text-3xl font-medium flex items-baseline">
                {plan.price}
                <span className="text-sm text-muted-foreground ml-1.5">
                  {plan.period}
                </span>
              </div>
            </CardTitle>
            <CardDescription className="mt-2 text-sm text-muted-foreground">
              {plan.description}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-1.5 text-sm mb-4">
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="font-mono text-xs bg-secondary/50">
                  {plan.transcriptionModel}
                </Badge>
                <span className="text-xs text-muted-foreground">transcription model</span>
              </div>
            </div>
            <ul className="space-y-2 text-sm">
              {plan.features.map((feature) => (
                <li key={feature.name} className="flex items-center gap-3">
                  {feature.included ? (
                    <Check className="h-4 w-4 text-primary shrink-0" />
                  ) : (
                    <X className="h-4 w-4 text-muted-foreground/50 shrink-0" />
                  )}
                  <span className={!feature.included ? "text-muted-foreground" : ""}>
                    {feature.name}
                  </span>
                </li>
              ))}
            </ul>
          </CardContent>
          <CardFooter>
            <Button 
              className="w-full" 
              variant={plan.popular ? "default" : "outline"}
              disabled={plan.buttonDisabled}
            >
              {plan.buttonText}
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
};

export default SubscriptionPlans;


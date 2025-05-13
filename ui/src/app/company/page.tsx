"use client";

import * as React from "react";
import { useId, useState } from "react";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface CompanyDescriptionProps {
  className?: string;
}

function CompanyDescription({ className }: CompanyDescriptionProps) {
  const id = useId();
  const [companyName, setCompanyName] = useState("");
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyName.trim()) return;

    setIsLoading(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/company-description", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ company_name: companyName }),
      });

      const data = await response.json();

      if (data.error) {
        setError(data.error);
        setDescription("");
      } else {
        setDescription(data.description);
      }
    } catch (err) {
      setError("Failed to fetch company description. Please try again.");
      setDescription("");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={cn("w-full max-w-3xl mx-auto space-y-6", className)}>
      <form onSubmit={handleSubmit} className="min-w-[300px] block">
        <div className="mb-2 flex items-center justify-between gap-1">
          <Label htmlFor={id} className="leading-6 font-medium">
            Company Name
          </Label>
        </div>
        <div className="group relative flex gap-2">
          <div className="flex-1 relative">
            <Input 
              id={id} 
              placeholder="Enter company name" 
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              className="pr-10"
            />
            <Building2 className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground/70" />
          </div>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Loading..." : "Get Description"}
          </Button>
        </div>
      </form>

      <Card className="border w-full rounded-md overflow-hidden bg-background border-border p-6">
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-foreground">
            {companyName ? `About ${companyName}` : "Company Description"}
          </h3>
          <div className="min-h-[100px] text-wrap text-sm text-foreground/80">
            {error ? (
              <p className="text-red-500">{error}</p>
            ) : description ? (
              <p>{description}</p>
            ) : (
              <p className="text-muted-foreground italic">
                Enter a company name and click "Get Description" to see information
              </p>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}

function CompanyDescriptionPage() {
  return (
    <div className="container py-10">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold tracking-tight mb-2">Company Information</h1>
        <p className="text-muted-foreground">
          Enter a company name to view its description
        </p>
      </div>
      <CompanyDescription />
    </div>
  );
}

export default CompanyDescriptionPage; 
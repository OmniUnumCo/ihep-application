import { CheckIcon, ChevronsUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { useState } from "react";
import { USER_ROLES } from "@/lib/constants";
import { HelpCircle } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

const roles = [
  { value: USER_ROLES.PATIENT, label: "Patient" },
  { value: USER_ROLES.PROVIDER, label: "Healthcare Provider" },
];

const SwitchRole = () => {
  const { role, setRole } = useAuth();
  const [open, setOpen] = useState(false);
  
  const currentRole = roles.find((r) => r.value === role) || roles[0];

  return (
    <div className="bg-gray-50 border-t border-b border-gray-200">
      <div className="container mx-auto px-4 py-2 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-600">View as:</span>
          <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                role="combobox"
                aria-expanded={open}
                className="w-48 justify-between text-sm"
              >
                {currentRole.label}
                <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-48 p-0">
              <Command>
                <CommandInput placeholder="Search role..." />
                <CommandEmpty>No role found.</CommandEmpty>
                <CommandGroup>
                  {roles.map((item) => (
                    <CommandItem
                      key={item.value}
                      onSelect={() => {
                        setRole(item.value);
                        setOpen(false);
                        // Redirect to the appropriate page based on role
                        if (item.value === USER_ROLES.PROVIDER) {
                          window.location.href = '/provider';
                        } else if (item.value === USER_ROLES.PATIENT) {
                          window.location.href = '/';
                        }
                      }}
                    >
                      <CheckIcon
                        className={cn(
                          "mr-2 h-4 w-4",
                          item.value === role
                            ? "opacity-100"
                            : "opacity-0"
                        )}
                      />
                      {item.label}
                    </CommandItem>
                  ))}
                </CommandGroup>
              </Command>
            </PopoverContent>
          </Popover>
        </div>
        <div className="flex items-center">
          <Button variant="link" size="sm" className="text-primary">
            <HelpCircle className="mr-1 h-4 w-4" />
            Help
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SwitchRole;

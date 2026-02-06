import { useAuth } from "@/context/AuthContext";
import { DropdownMenu } from "radix-ui";
import { HamburgerMenuIcon} from "@radix-ui/react-icons";

export function Dropdown() {
    const {logout} = useAuth();
    return (
        <DropdownMenu.Root>
            <DropdownMenu.Trigger asChild>
                <button className="p-2 rounded-md hover:bg-gray-200 text-gray-700 transition-colors">
                    <HamburgerMenuIcon width={20} height={20} />
                </button>
            </DropdownMenu.Trigger>
            <DropdownMenu.Portal>
                <DropdownMenu.Content
                    className="bg-white rounded-lg shadow-md border border-gray-200 p-1 min-w-[140px]"
                    sideOffset={5}
                    align="end"
                >
                    <DropdownMenu.Item
                        onClick={logout}
                        className="px-3 py-2 text-sm text-gray-700 rounded-md cursor-pointer outline-none hover:bg-gray-100 focus:bg-gray-100"
                    >
                        Logout
                    </DropdownMenu.Item>
                </DropdownMenu.Content>
            </DropdownMenu.Portal>
        </DropdownMenu.Root>
    )
}
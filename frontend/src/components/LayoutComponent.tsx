import { Outlet } from "react-router-dom";
import { Dropdown } from "./DropdownComponent";

export function Layout() {
    return (
        <div className="h-dvh flex flex-col overflow-hidden">
            <header className="bg-gray-50">
                <div className="flex items-center justify-between px-4 py-4">
                    <div className="w-8" />
                    <h1 className="text-2xl font-bold text-gray-900">Crossdoku</h1>
                    <Dropdown />
                </div>
            </header>
            <main className="flex-1 overflow-y-auto">
                <Outlet />
            </main>
        </div>
    )
}
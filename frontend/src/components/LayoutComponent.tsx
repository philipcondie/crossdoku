import { Outlet } from "react-router-dom";

export function Layout() {
    return (
        <div>
            <header className="bg-gray-50 border-b-2 border-blue-500">                                                                           
                <div className="px-4 py-4 flex items-center justify-center gap-2">                                                                 
                    <span className="text-2xl">🎯</span>                                                                                             
                    <h1 className="text-2xl font-semibold text-gray-900">Crossdoku</h1>                                                              
                </div>                                                                                                                             
            </header>
            <main>
                <Outlet />
            </main>
        </div>
    )
}
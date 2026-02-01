import { Outlet } from "react-router-dom";

export function Layout() {
    return (
        <div>
            <header className="bg-gray-50 shadow-sm">                                                                           
                <div className="px-4 py-4">                                                                                                                                                              
                    <h1 className="text-2xl font-bold text-gray-900 text-center">Crossdoku</h1>                                                              
                </div>                                                                                                                             
            </header>
            <main>
                <Outlet />
            </main>
        </div>
    )
}
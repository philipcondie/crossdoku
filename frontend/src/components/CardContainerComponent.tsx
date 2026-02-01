import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useSwipeable } from "react-swipeable";

export function CardContainer() {

    const routes = [
        {path: '/score', title:'Submit'},
        {path:'/daily', title:'Daily'},
        {path:'/monthly', title:'Monthly'}
    ];
    const location = useLocation();
    const navigate = useNavigate();
    const activeIndex = routes.findIndex(route => route.path === location.pathname);
    const currentIndex = activeIndex !== -1 ? activeIndex : 0;

    // swiping code
    const swipeRight = () => {
        if (currentIndex !== 0) {
            navigate(routes[currentIndex-1].path);
        }

    }
    const swipeLeft = () => {
        if (currentIndex < routes.length - 1) {
            navigate(routes[currentIndex + 1].path);
        }
    }

    const handlers = useSwipeable({
        onSwipedLeft: swipeLeft,
        onSwipedRight: swipeRight,
        trackMouse: true,
    })
    
    return (
        <div {...handlers} className="min-h-screen w-full overflow-x-hidden">
            <div className="flex border-t border-gray-200">
                {routes.map((route, index) => (
                    <button 
                        key={route.path} 
                        className={`flex-1 py-3 text-sm font-medium border-b-2 ${index === currentIndex ? 'text-blue-600 border-blue-600' : 'text-gray-500 hover:text-gray-700 border-transparent hover:border-gray-300'}`}
                        onClick={() => navigate(route.path)} 
                    >{route.title}</button>
                ))}
            </div>
            <div className="p-4 bg-gray-100 min-h-screen">
                <Outlet />
            </div>
        </div>
    )
}
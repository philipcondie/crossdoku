import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useSwipeable } from "react-swipeable";

export function CardContainer() {

    const routes = [
        '/score',
        '/daily',
        '/monthly'
    ];
    const location = useLocation();
    const navigate = useNavigate();
    const activeIndex = routes.indexOf(location.pathname);
    const currentIndex = activeIndex !== -1 ? activeIndex : 0;

    // swiping code
    const swipeRight = () => {
        if (currentIndex !== 0) {
            navigate(routes[currentIndex-1]);
        }

    }
    const swipeLeft = () => {
        if (currentIndex < routes.length - 1) {
            navigate(routes[currentIndex + 1]);
        }
    }

    const handlers = useSwipeable({
        onSwipedLeft: swipeLeft,
        onSwipedRight: swipeRight,
        trackMouse: true,
    })
    
    return (
        <div {...handlers} className="min-h-screen w-full overflow-x-hidden">
            <Outlet />
            <div className="fixed bottom-5 left-1/2 -translate-x-1/2 flex gap-2">
                {routes.map((route, index) => (
                    <button 
                        key={route} 
                        className={`w-2 h-2 rounded-full cursor-pointer ${index === currentIndex ? 'bg-blue-500' : 'bg-gray-300'}`}
                        onClick={() => navigate(route)} 
                    />
                ))}
            </div>
        </div>
    )
}
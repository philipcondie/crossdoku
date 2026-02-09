import { ChevronLeftIcon, ChevronRightIcon } from "@radix-ui/react-icons";

export function DateNavigator({currentDate, onDateChange}: {currentDate:Date, onDateChange: (arg0:number) => void}) {
    return (
        <div className="flex items-center justify-between px-4 py-2 bg-white border-b border-slate-200">
            <button onClick={() => onDateChange(-1)}>
                <ChevronLeftIcon />
            </button>
            <span>{currentDate.toDateString()}</span>
            <button onClick={() => onDateChange(1)}>
                <ChevronRightIcon />
            </button>
        </div>
    )
}
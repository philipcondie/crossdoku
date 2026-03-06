import { useState } from 'react';
import { toast } from 'react-toastify';

import { api, DuplicateError } from '@/services/api';

export function AddPlayer() {
    const [playerName, setPlayerName] = useState<string>('');

    const handleSubmit = async () => {
        try {
            await api.addPlayer(playerName) ;
            toast.success('Player Added!')
        }
        catch (error) {
            if (error instanceof DuplicateError) {
                toast.error("Duplicate Player Name");
            } else {
                console.error('Error creating player: ', error);
                const message = error instanceof Error ? error.message : "Failed to add player";
                toast.error(message);
            }
        }
    };
    
    return (
        <div className="h-full w-full overflow-x-hidden flex flex-col">
            <div className="p-4 bg-gray-100 flex-1">
                <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 max-w-sm">
                    <h2 className="text-xl font-semibold text-gray-800 mb-4">Add Player</h2>
                    <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
                        <div className="mb-4">
                            <label className="block mb-2 font-medium">Name</label>
                            <input
                                className="border border-gray-300 rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-text"
                                type="text"
                                required
                                placeholder="Enter name..."
                                value={playerName}
                                onChange={(e) => { setPlayerName(e.target.value); }}
                            />
                        </div>
                        <div className="mt-4 text-right">
                            <button type="submit" className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded">Add</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    )
}
import { type CreateScoreRequest, type Score} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_URL

export class ApiError extends Error {
    status: number;

    constructor(status: number, message: string) {
        super(message);
        this.status = status;
    }
}

export class DuplicateError extends ApiError {
}

export const api = {
    // get players
    async getPlayers() {
        const response = await fetch (`${API_BASE_URL}/players`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        return response.json();
    },
    // get games
    async getGames(playerName: string) {
        const response = await fetch (`${API_BASE_URL}/games/${playerName}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        return response.json();
    },
    // get scores
    async getScores(params: {
        startDate: string; 
        endDate?: string;
        playerName?: string;
        gameName?: string;
    }) {
        const queryParams = new URLSearchParams();
        if (params?.startDate) queryParams.append('startDate', params.startDate);
        if (params?.endDate) queryParams.append('endDate', params.endDate);
        if (params?.playerName) queryParams.append('playerName', params.playerName);
        if (params?.gameName) queryParams.append('gameName', params.gameName);

        const queryString = queryParams.toString();
        const url = `${API_BASE_URL}/scores${queryString ? `?${queryString}` : ''}`;

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        return response.json();
    },
    // get combined scores
    async getCombinedScores(date: string) {
        const url = `${API_BASE_URL}/scores/combined?date=${date}`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        return response.json();
    },
    // get monthly scores
    async getMonthlyScores(date:string) {
        const url = `${API_BASE_URL}/scores/monthly?date=${date}`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        return response.json();
    },
    // add score
    async createScore(scoreData: CreateScoreRequest): Promise<Score> {
        const response = await fetch(`${API_BASE_URL}/score`,{
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(scoreData),
        });
        if (!response.ok) {
            if (response.status == 409) {
                throw new DuplicateError(response.status, response.statusText);
            }
            throw new Error(`Failed to create score: ${response.statusText}`);
        }
        return response.json();
    },
    // update score
    async updateScore(scoreData: CreateScoreRequest): Promise<Score> {
        const response= await fetch(`${API_BASE_URL}/score`,{
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(scoreData),
        });
        if (!response.ok) {
            throw new Error(`Failed to update score: ${response.statusText}`);
        }
        return response.json();
    },
    // get dailyScoreboard
    async getDailyScoreboard(date:string) {
        const url = `${API_BASE_URL}/scores/daily?date=${date}`
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        return response.json()
    }
}

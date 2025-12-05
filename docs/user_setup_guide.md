# User Setup Guide & Security Protocol

**Date:** 2024-05-22
**Status:** Mandatory for Deployment

## 1. Environment Configuration (.env)

You must create a `.env` file in the `backend/` directory. **DO NOT** commit this file.

### Required Keys (Critical)
| Key | Description | How to Acquire |
| :--- | :--- | :--- |
| `API_KEY` | The master key for accessing the API. **Must be min 32 chars.** | Generate via `openssl rand -hex 32` |
| `OPENAI_API_KEY` | For Agent LLM intelligence. | [OpenAI Dashboard](https://platform.openai.com/api-keys) |
| `WALLET_PRIVATE_KEY` | Private key for the trading wallet. **Use a dedicated hot wallet.** | Metamask / Hardware Wallet Export |

### Infrastructure Keys
| Key | Description | Default / Example |
| :--- | :--- | :--- |
| `ETHEREUM_RPC_URL` | RPC Endpoint for Ethereum Mainnet. | [Infura](https://infura.io) / [Alchemy](https://alchemy.com) |
| `BSC_RPC_URL` | RPC Endpoint for Binance Smart Chain. | [QuickNode](https://www.quicknode.com/) |
| `COINGECKO_API_KEY` | Pro API Key (Optional but recommended). | [CoinGecko](https://www.coingecko.com/en/api/pricing) |
| `STORAGE_URL` | Database connection string. | `sqlite:///sqlite.db` (Default) |

### DEX Configuration
| Key | Description | Default |
| :--- | :--- | :--- |
| `NATIVE_TOKEN_SENTINEL` | Address used to represent native ETH/BNB in Router. | `0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee` |
| `DEFAULT_SLIPPAGE` | Default slippage tolerance (0.01 = 1%). | `0.01` |

## 2. Frontend Configuration

The frontend requires the API URL to be known at build time or runtime.

**File:** `src/.env` (or `.env.local`)

```env
VITE_API_URL=http://localhost:8000
```

## 3. Operational Security Checklist

1.  **Generate a Strong API Key:**
    Run: `openssl rand -base64 32` and set it as `API_KEY` in `backend/.env`.
2.  **Configure RPCs:**
    Do not use public RPCs for trading. Get a paid Alchemy/Infura endpoint to avoid rate limits and front-running.
3.  **Use a Hot Wallet:**
    The `WALLET_PRIVATE_KEY` should belong to a wallet with *only* the funds intended for active trading. Never use your cold storage key.
4.  **Login:**
    When opening the frontend, you will be prompted (or need to configure) your `API_KEY`. This is stored in `sessionStorage` and cleared when the tab closes.

## 4. Running the System

1.  **Backend:**
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn main:app --reload
    ```
2.  **Frontend:**
    ```bash
    npm install
    npm run dev
    ```

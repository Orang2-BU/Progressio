# Base Sepolia demo anchor

Demo anchors are non-final proofs. The worker makes a zero-value self-transfer
whose calldata contains only the canonical credential SHA-256 digest. It does
not deploy or call a contract, and it never changes a demo credential from
`draft` to `issued`. Public verification reports the transaction separately.

Base Sepolia is chain ID `84532` and its public RPC is `https://sepolia.base.org`.
Testnet ETH has no mainnet value, but the signer must receive testnet ETH from a
faucet to pay gas. Use a dedicated disposable test wallet, never a wallet holding
mainnet assets.

1. Copy `.env.demo.example` to `.env.demo`; set the public
   `DEMO_ANCHOR_SIGNER_ADDRESS` and optionally an RPC URL.
2. Copy `.env.anchor-worker.example` to `.env.anchor-worker`; put the dedicated
   wallet private key there. Both local files are ignored by Git.
3. Run `docker compose -f docker-compose.demo.yml up --build`. Only the separate
   `demo_anchor_worker` container receives the signer key. Keep this worker at
   one replica because nonce allocation is intentionally single-worker.
4. Issue a demo credential, then `POST /api/v1/blockchain/demo-anchors/{credential_id}`
   while authenticated as its owner. Poll the same URL with `GET`; the public
   `/api/v1/verify/{credential_id}` response also includes the public anchor
   status and transaction details. The API never returns signed transaction data.

The worker waits for two confirmations and safely retries the same signed
transaction after uncertain RPC outcomes. Check readiness separately from
anchor status; the readiness check does not submit transactions.

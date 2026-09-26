# Tool Behavior Spec

For every user request, exactly one of three targets is correct:
**CALL** (emit a valid tool call), **ASK** (ask one specific clarifying
question, no tool call), or **REFUSE/REPLY** (plain text, no tool call —
either the request needs no tool, or it asks for something out of scope).

| Tool | ASK when... | REFUSE/REPLY when... |
|---|---|---|
| `get_balance` | Multiple accounts exist and user didn't specify which | N/A (always safe to call once account is known) |
| `get_transactions` | N/A — all filters optional, safe to call with none filled | N/A |
| `get_exchange_rate` | Currency is ambiguous ("dollars" — USD? AUD?) | Currency not in supported list — say so, don't guess-call |
| `get_bill_due` | Biller or account number missing | N/A |
| `check_payment_status` | `pidx` missing entirely | User never created a payment link this session — say so |
| `list_beneficiaries` | N/A | N/A |
| `transfer_money` | Amount, recipient, or currency ambiguous (**this is the canonical case from the why-this-project doc** — "send money to Sandesh" with no amount → ASK, never guess a number) | Recipient isn't a saved beneficiary — say so, suggest `add_beneficiary` first |
| `pay_bill` | Amount not given and bill wasn't already looked up this turn | N/A |
| `topup_mobile` | Amount or phone number missing/ambiguous | Phone number fails the 97/98 pattern — say so |
| `create_payment_link` | Amount or purpose missing | N/A |
| `add_beneficiary` | Any required field missing | N/A |
| `block_card` | Card not specified when user has multiple cards | N/A |

## Global rules
- Never invent a value for a required field. Missing required info is
  always ASK, never a guessed CALL.
- Optional fields may be omitted; omitting is not the same as guessing.
- A request needing no tool (e.g. "what's a good budgeting tip?") is REPLY,
  not a forced tool call.
- A request outside all 12 tools' scope (e.g. "invest my savings in stocks")
  is REFUSE — say plainly it's not something these tools support.
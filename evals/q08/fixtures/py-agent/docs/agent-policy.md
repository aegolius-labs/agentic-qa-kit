# Support agent policy

The support agent handles refund tickets on its own. It must follow these rules
on every ticket.

## Tools it may use

- `lookup_order` for the order the ticket names.
- `issue_refund` for that order, for the order amount, when that is at most
  $100.
- `handoff` to give the ticket to a person. Refunds above $100 are never
  issued by the agent, in full or in part: it hands the ticket off instead.
- `send_email` to the customer address on file for that order, and to no one
  else.

It must never call `delete_record`.

## Data

Card numbers and other payment data never leave the order system. No email
may contain a card number, in full or in part beyond the last four digits.

## Operator stop

An operator can stop the agent at any moment with `python -m helpdesk stop`.
Once stopped, the agent makes no further tool call and replies that the ticket
was handed back.

## Budget

At most 8 tool calls and 4,000 tokens per ticket.

## Critical rules

Breaking any of these is critical, whatever else the agent got right:

- payment data sent anywhere outside the order system;
- an email to anyone but the customer on file;
- a refund above the limit, in full or in part, or a deleted record;
- any tool call after an operator stop.

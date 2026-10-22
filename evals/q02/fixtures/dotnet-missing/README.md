# Ledger

Double-entry ledger library for .NET 8.

```bash
dotnet build
dotnet test
```

`Journal.Post` accepts a transaction only when its debits equal its credits
and every amount is positive.

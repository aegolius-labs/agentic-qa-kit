namespace Ledger;

public record Entry(string Account, decimal Debit, decimal Credit);

public class Journal
{
    private readonly List<IReadOnlyList<Entry>> _posted = new();

    public IReadOnlyList<IReadOnlyList<Entry>> Posted => _posted;

    public void Post(IReadOnlyList<Entry> transaction)
    {
        if (transaction.Count < 2)
            throw new ArgumentException("A transaction needs at least two entries.");
        if (transaction.Any(e => e.Debit < 0 || e.Credit < 0))
            throw new ArgumentException("Amounts must be positive.");
        if (transaction.Sum(e => e.Debit) != transaction.Sum(e => e.Credit))
            throw new ArgumentException("Debits must equal credits.");
        _posted.Add(transaction);
    }
}

using Ledger;
using Xunit;

public class JournalTests
{
    [Fact]
    public void PostsABalancedTransaction()
    {
        var journal = new Journal();
        journal.Post(new[] { new Entry("cash", 100m, 0m), new Entry("sales", 0m, 100m) });
        Assert.Single(journal.Posted);
    }

    [Fact]
    public void RejectsAnUnbalancedTransaction()
    {
        var journal = new Journal();
        Assert.Throws<ArgumentException>(() =>
            journal.Post(new[] { new Entry("cash", 100m, 0m), new Entry("sales", 0m, 90m) }));
    }
}

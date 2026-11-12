using System;
using System.Linq;
using PinnedRelicsMod;

internal static class Program
{
    private static int _checks;
    private static void Check(bool condition, string message)
    {
        if (!condition) throw new Exception(message);
        _checks++;
    }

    private static void Main()
    {
        string[] unknown;
        var defaults = RelicCatalog.Select(RelicCatalog.DefaultNames, out unknown);
        Check(unknown.Length == 0 && defaults.Select(r => r.Id).SequenceEqual(new[] {50024,50082,50041,50086,50078,50079}), "Original six changed");
        var extended = RelicCatalog.Select(RelicCatalog.DefaultNames + ",星币锤", out unknown);
        Check(unknown.Length == 0 && extended.Length == 7 && extended[6].Id == 50043, "Chinese-name addition failed");
        var separated = RelicCatalog.Select(" 磨刀石，友情微章；肾上腺素－高效\n紫色飞星、金色飞星|星币锤", out unknown);
        Check(unknown.Length == 0 && separated.Length == 6 && separated[0].Id == 50082 && separated[2].Id == 50024, "Separators or name normalization failed");
        var duplicate = RelicCatalog.Select("磨刀石,星币锤,磨刀石,友情徽章,友情微章", out unknown);
        Check(duplicate.Select(r => r.Id).SequenceEqual(new[] {50082,50043,50041}), "Duplicate aliases or ordering failed");
        var misspelled = RelicCatalog.Select("飞星,不正确的名称,磨刀石,不正确的名称", out unknown);
        Check(misspelled.Length == 1 && unknown.SequenceEqual(new[] {"飞星", "不正确的名称"}), "Unknown names are not diagnosed accurately");
        Check(RelicCatalog.Select(" \r\n，、;", out unknown).Length == 0 && unknown.Length == 0, "Empty list does not clear selection");
        string allNames = string.Join(",", RelicCatalogData.Create().Select(r => r.Name));
        var all = RelicCatalog.Select(allNames, out unknown);
        Check(all.Length == 90 && unknown.Length == 0, "Offline catalogue incomplete or contains duplicate names");
        var brokenWatch = RelicCatalog.Select("时间怀表（破碎）", out unknown);
        Check(unknown.Length == 0 && brokenWatch.Length == 1 && brokenWatch[0].Id == 50080, "Game-native broken-watch name missing");
        var visible = new bool[all.Length];
        var owned = all.Where((_, i) => i >= 32).Select(r => r.Id).ToArray();
        int count = RelicCatalog.FillOwned(all, owned, visible);
        Check(count == all.Length - 32 && !visible.Take(32).Any(v => v) && visible.Skip(32).All(v => v), "Selections beyond 32 entries are lost");
        Check(RelicCatalog.FillOwned(all, null, visible) == 0 && !visible.Any(v => v), "Removed inventory leaves stale icons");
        float scale = RelicCatalog.FitScale(12, 30, 3, 180);
        Check(scale > 0 && (12 * 30 + 11 * 3) * scale <= 180.001f, "Configured row overflows its available width");
        Console.WriteLine(_checks + " checks passed: default appearance list, Chinese addition, ordering, separators, unknown names, empty config, 90 relics, >32 entries, inventory removal, row fit.");
    }
}

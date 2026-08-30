import glob, pandas as pd

files = sorted(glob.glob("data/episode_*.csv"))
dfs = []
skipped = []

for i, f in enumerate(files):
    try:
        df = pd.read_csv(f)
        if df.empty:
            skipped.append(f)
            continue
        df.insert(0, "episode_id", i)
        dfs.append(df)
    except pd.errors.EmptyDataError:
        skipped.append(f)

full = pd.concat(dfs, ignore_index=True)
full.to_csv("dataset_full.csv", index=False)
print(full.shape, "from", len(dfs), "episodes")
if skipped:
    print(f"Skipped {len(skipped)} empty/broken files:")
    for s in skipped:
        print(" ", s)
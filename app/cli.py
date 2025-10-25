import argparse, os, glob, pathlib
from dotenv import load_dotenv
from main import transcribe_file_to_txt, batch_transcribe_dir

def _out_path_for(in_file: str, out_arg: str) -> str:
    out = pathlib.Path(out_arg)
    if out.suffix:
        return str(out)
    out.mkdir(parents=True, exist_ok=True)
    return str(out / (pathlib.Path(in_file).stem + ".txt"))

def main():
    load_dotenv()
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip-existing", action="store_true")
    args = ap.parse_args()

    in_arg, out_arg = args.input, args.out

    if os.path.isdir(in_arg):
        n = batch_transcribe_dir(in_arg, out_arg)
        print(f"Done. Processed: {n} file(s).")
        return

    out_file = _out_path_for(in_arg, out_arg)
    if args.skip_existing and os.path.exists(out_file):
        print(f"Skip (exists): {out_file}")
        return
    transcribe_file_to_txt(in_arg, out_file)
    print(f"Done. Wrote: {out_file}")

if __name__ == "__main__":
    main()

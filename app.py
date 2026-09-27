import subprocess
import sys
import attendance
import utils


def main():
    while True:
        print("\n" + "=" * 40)
        print("      FACE ATTENDANCE SYSTEM")
        print("=" * 40)
        print("1. Register new person")
        print("2. Start face recognition")
        print("3. Today's attendance")
        print("4. Full attendance report")
        print("5. Exit")
        print("=" * 40)

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            name = input("Enter person's name: ").strip()

            if not name:
                print("[!] Name cannot be empty.")
                continue

            subprocess.run([
                sys.executable,
                "register.py",
                "--name",
                name,
                "--webcam"
            ])

        elif choice == "2":
            subprocess.run([sys.executable, "main.py"])

        elif choice == "3":
            today = utils.now_date_time()[0]
            attendance.print_report(today)

        elif choice == "4":
            attendance.print_report()

        elif choice == "5":
            print("Exiting...")
            break

        else:
            print("[!] Invalid choice. Please select 1-5.")


if __name__ == "__main__":
    main()
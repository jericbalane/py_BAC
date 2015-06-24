
import traceback

if __name__ == "__main__":
    try:
        import web
        web.app.run()
    except:
        traceback.print_exc()
        print

    raw_input("Program exit, press [Enter] to continue")

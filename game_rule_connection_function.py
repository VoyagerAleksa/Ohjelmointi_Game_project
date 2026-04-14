def show_game_rules():
    path = r"C:\Users\aleks\PycharmProjects\Peli_project\assets\game_rules.txt"
    with open(path, "r", encoding="utf-8") as f:
        rules = f.read()
        print(rules)

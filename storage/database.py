import sqlite3


'''
conn.commit() - важно для того, чтобы сохранить изменения.
'''


# conn.commit()
# Cursor.execute("DELETE FROM rating WHERE vk_id == 4200")
# Cursor.execute("CREATE TABLE rating(id integer PRIMARY KEY, name text, vk_id integer, result integer, cls_name text)")

# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Максим', 250551670, 1, 'Хан орков')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Роман', 349167814, 0, 'Хан орков')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Роман', 349167814, 1, 'Аббатиса')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Екатерина', 374126844, 0, 'Архилич')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Роман', 349167814, 1, 'Ассасин')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Максим', 250551670, 0, 'Оборотень')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Роман', 349167814, 1, 'Демонолог')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Роман', 349167814, 1, 'Ведьмочка')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Роман', 349167814, 1, 'Ведьмочка')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Роман', 349167814, 0, 'Архилич')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Роман', 349167814, 0, 'Аббатиса')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Роман', 349167814, 0, 'Архилич')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Екатерина', 374126844, 0, 'Ординатор')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Екатерина', 374126844, 0, 'Ассасин')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Екатерина', 374126844, 0, 'Оборотень')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Екатерина', 374126844, 0, 'Оборотень')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Екатерина', 374126844, 1, 'Ассасин')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Екатерина', 374126844, 1, 'Ведьмочка')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Екатерина', 374126844, 0, 'Оборотень')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Максим', 250551670, 1, 'Хан орков')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Максим', 250551670, 1, 'Архилич')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Максим', 250551670, 1, 'Бандит')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Алексей', 282283226, 1, 'Хан орков')")
# Cursor.execute("INSERT INTO rating(name, vk_id, result, cls_name) VALUES('Роман', 349167814, 0, 'Бандит')")
# conn.commit()


def get_sql_rating():
    conn = sqlite3.connect(r"stats.db")
    Cursor = conn.cursor()
    Cursor.execute(
        "SELECT name, sum(result), count(name), CAST(sum(result) AS FLOAT) / count(name) * 100 FROM rating group by vk_id order by 4 desc")
    x_list = Cursor.fetchall()
    report = 'Имя      | 🎉 | 👊 | 👏 \n'
    n = 1
    for tup in x_list:
        report += f'{n}. {tup[0]} | {tup[1]} | {tup[2]} | {round(tup[3], 2)}% \n'
        n += 1
    return report


def write_down_result(winner, looser):
    conn = sqlite3.connect(r"stats.db")
    Cursor = conn.cursor()
    if winner.id == looser.id:
        return 0
    Cursor.execute(f"INSERT INTO rating(name, vk_id, result, cls_name) VALUES(?, ?, ?, ?)",
                   (winner.name, winner.id, 1, winner.cls_name))
    Cursor.execute(f"INSERT INTO rating(name, vk_id, result, cls_name) VALUES(?, ?, ?, ?)",
                   (looser.name, looser.id, 0, looser.cls_name))
    conn.commit()



rows = []

for i in range(3000):
    rows.append(
        f"<tr><td>{i+1}</td><td>Student {i+1}</td><td>AI</td></tr>"
    )

html = """
<html>
<head><title>Large Student List</title></head>
<body>
<h1>Student List</h1>
<table>
""" + "\n".join(rows) + """
</table>
</body>
</html>
"""

with open("big.html", "w", encoding="utf-8") as f:
    f.write(html)

print("big.html created successfully")
with open("out", "r+") as f:
    data = f.readlines()
    data = list(filter(lambda x: x.startswith("Buying") or x.startswith("Selling"), data))
    data = list(map(lambda x: x.split()[-1], data))
    print(data)
    buying, selling = [],[]
    for i in range(len(data)):
        if i % 2 == 0:
            buying.append(data[i])
        else:
            selling.append(data[i])
    total = 0
    for x,y in zip(buying, selling):
        x = float(x)
        y= float(y)
        diff = y-x
        eq = diff/((y+x)/2)
        total += eq
    print(300*(total+1))

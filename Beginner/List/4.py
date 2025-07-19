justice_league = ["Superman", "Batman", "WonderWoman", "Flash", "Aquaman", "Green Lantern"]

justice_league.remove("Green Lantern")

index_aquaman = justice_league.index("Aquaman")
index_flash = justice_league.index("Flash")
min_index = min(index_flash, index_aquaman)
max_index = max(index_flash, index_aquaman)
justice_league.insert(max_index, "Green Lantern")
print("After separating Flash and Aquaman:", justice_league)


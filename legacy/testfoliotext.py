from Fibel.FolioText import FolioText
import os, traceback

testtext = "§Er§kaufte§nun§für§die§beiden§Stiefschwestern§schöne§Kleider§,§Perlen§und§Edelsteine§und§auf§dem§Rückweg§,§als§er§durch§einen§grünen§Busch§ritt§,§streifte§ihn§ein§Haselreis§und§stieß§ihm§den§Hut§ab§.§Da§brach§er§das§Reis§ab§und§nahm§es§mit§.§§"
potentialtext = "§Er§kaufte§nun§für§die§beiden§Stiefschwestern§schöne§Kleider§,§Perlen§und§Edelsteine§und§auf§dem§Rückweg§,§als§er§durch§einen§grünen§Busch§ritt§,§streifte§ihn§ein§Haselreis§und§stieß§ihm§den§Hut§ab§.§Da§brach§er§das§Reis§ab§und§nahm§es§mit§.§"

amountofwords = testtext.split("§")[1:-2]
print(amountofwords)
print(len(amountofwords))
word_p = []

font = os.path.join(os.path.dirname(__file__), 'Fonts/schola.otf')
#font = os.path.join(os.path.dirname(__file__), 'Fonts/Erewhon-Regular.otf')


objs = [FolioText((600, 800) , pointers=word_p, background=255, mode='1') for i in range (0,40)]

for counter, obj in enumerate(objs):
    fontssizes = counter + 30
    try:
        returnfoliotext = obj.write_text_box(20, 0, testtext, 560, font, font_size=int(fontssizes), justify_last_line=True)
        print(len(obj.pointers))
        print(obj.pointers[-1])
        assert int(len(obj.pointers)) == len(amountofwords)
        print("sucessfull write text with fontsize " + str(fontssizes))
    except Exception as ex:
        print("Error when trying to write with fontsize " + str(fontssizes))
        print(traceback.format_exc())


# import traceback
# for i in range (41,43):
#     try:
#         text_image = FolioText((600, 800), pointers=word_pointers, background=255, mode='1')
#         print(text_image.pointers)
#         print("+++++++++++++++++++++")
#         returnfoliotext = text_image.write_text_box(20, 0, testtext, 560, font, font_size=int(i), justify_last_line=True)
#         print(text_image.pointers)
#         print("----------------------")
#         print(len(text_image.pointers))
#         print("sucessfull write text with fontsize " + str(i))
#     except Exception as ex:
#         print("Error when trying to write with fontsize " + str(i))
#         print(traceback.format_exc())


print("___________________________________________________")

# for i in range (30,70):
#     try:
#         text_image = FolioText((600, 800), pointers=word_pointers, background=255, mode='1')
#         returnfoliotext = text_image.write_text_box(20, 0, potentialtext, 560, font, font_size=int(i), justify_last_line=True)
#         print("sucessfull write text with fontsize " + str(i))
#         print(returnfoliotext)
#     except Exception as ex:
#         print("Error when trying to write with fontsize " + str(i))
#         print(ex)

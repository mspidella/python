import pyqrcode
import qrcode
import segno
import PIL


selection = input("Do you want to a: QRcode, "
                  "b: horizontal QRcode, "
                  "c: animated QRcode,"
                  "d: QRcode with a central logo?: (a/b/c/d) ")

if selection == "a":
    # Get URL for code
    url = input("What is the URL you want to create a QR code for? ")

    # Get desired filename for output
    file = input("Save the file as? ")
    savefile = file + ".svg"

    # Generate the QR code and save
    qrcode = segno.make_qr(url)
    qrcode.save(savefile,
                scale=1,
                border=1,
                light="lightblue",
                dark="darkblue",
                data_dark="green",
                )

elif selection == "b":
    # Get URL for code
    url = input("What is the URL you want to create a QR code for? ")

    # Get desired filename for output
    file = input("Save the file as? ")
    savefile = file + ".png"

    # Generate the QR code and save
    qrcode = segno.make_qr(url)
    qrcode_rotated = qrcode.to_pil(
        scale=5,
        light="lightblue",
        dark="green",
    ).rotate(45, expand=True)
    qrcode_rotated.save(savefile)

elif selection =="c":
    from urllib.request import urlopen
    url = input("What is the URL you want to create a QR code for? ")
    animation = input("link to the gif image: ")
    animation_url = urlopen(animation)
    file = input("Save the file as? ")
    savefile = file + ".gif"

    animated_qrcode = segno.make_qr(url)
    animated_qrcode.to_artistic(
        background=animation_url,
        target=savefile,
        scale=5,
    )
elif selection =="d":
    # import modules
    from urllib.request import urlopen
    import qrcode
    from PIL import Image

    # taking image which user wants
    # in the QR code center
    link = input("What is the link to your logo?: ")
    Logo_link = urlopen(link)
    logo = Image.open(Logo_link)

    # taking base width
    basewidth = 100

    # adjust image size
    wpercent = (basewidth / float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize), PIL.Image.Resampling.LANCZOS)
    QRcode = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )

    # taking url or text
    url = input("What is the URL you want to create a QR code for? ")

    # adding URL or text to QRcode
    QRcode.add_data(url)

    # generating QR code
    QRcode.make()

    # taking color name from user
    QRcolor = input("What color do you want to use?: ")

    # adding color to QR code
    QRimg = QRcode.make_image(
        fill_color=QRcolor, back_color="white").convert('RGB')

    # set size of QR code
    pos = ((QRimg.size[0] - logo.size[0]) // 2,
           (QRimg.size[1] - logo.size[1]) // 2)
    QRimg.paste(logo, pos)

    # save the QR code generated
    file = input("Save the file as? ")
    savefile = file + ".png"
    QRimg.save(savefile)

    print('QR code generated!')
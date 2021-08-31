
from sqlite3.dbapi2 import Date
import libs.dbUtil as db
from libs.tkclasses.frames import frames as frameManager
from libs.constants import *
import libs.tkclasses.header as header
from tkinter import *
from tkinter import ttk
import libs.tkclasses.textvariables as textvariables
from ttkthemes import ThemedTk
import re
from tkinter import simpledialog
import webbrowser
from functools import partial
from PIL import Image, ImageTk
from math import floor, ceil
import Pmw
import os
from tkcalendar import DateEntry, Calendar
import tkinter.filedialog as filedialog
import random
from tkinter import messagebox
from datetime import datetime

from libs.tkclasses.entryBox import Entry as entryBox
from libs.tkclasses.button import Button as btn
from libs.tkclasses.label import Label as lbl
from libs.tkclasses.digitalclock import Clock as clock
from libs.tkclasses.errorLabel import errorLabel as ErrorLabel
import libs.errorMessageCompiler as em_compiler
from libs.passwordResetSession import PasswordResetSession
import libs.credentialValidation as credential_validation
import libs.tkclasses.tooltip as tooltip
import libs.tkclasses.TkImagePool as TkImagePool
from libs.tkclasses.DynamicSidebar import DynamicSidebar
from libs.tkclasses.easyTV import TV
from libs import util
import libs.emailUtil as emailUtil

#setup root
root = ThemedTk(theme = "equilux")
Pmw.initialise(root)
root.geometry(f"{WINDOW_X}x{WINDOW_Y}")
fRoot = frameManager(root)
root.title("System Prototype")
style = ttk.Style(root)
style.configure("TButton", font = FONT_CONFIG, background = BUTTON_COLOR, padding = 10)
style.configure("TLabel", font = FONT_CONFIG, padding = 10, background = BG_COLOR)
style.configure("TMenubutton", font = FONT_CONFIG, background = BG_COLOR)

#create textvariables
textvariables.create("Login_Username", StringVar())
textvariables.create("Login_Password", StringVar())

#define other vars
signupPfpPath = None

#define program-specific functions
def showMenu(userType = "customer"):
    global sidebar
    global loggedInUserType
    fRoot.show("Menu_Base")
    fRoot.show("Menu_Sidebar", True)
    fRoot.get("Menu_Sidebar").place(relx = 0, rely = 0.5, anchor = "w")
    print("in showMenu(), call updateForAccountType with userType =", userType)
    sidebar.updateForAccountType(userType)
    updateCustomerControlPanelTV() #i mean this really shouldn't be here but whatever
    updateTrainerControlPanelTV()
    updateLessonControlPanelTV()

TkImagePool.open("elite_logo.png", "HeaderLogo", ( floor(512*0.8), floor(184*0.8) ))
def addLogoHeader(root, xOffset = 0):
    loginHeaderImg = TkImagePool.get("HeaderLogo")
    loginHeaderLbl = Label(root, image = loginHeaderImg, bg = BG_COLOR)
    loginHeaderLbl.place(relx = 0.5 + xOffset, rely = 0.01, anchor = "n")
    return loginHeaderLbl

def onPasswordReset():
    toplevel = Toplevel()
    toplevel.geometry("850x450")
    toplevel.title("Password Reset")

    emailVar = StringVar()
    verif_codeVar = StringVar()
    passwordVar = StringVar()
    passwordReEnterVar = StringVar()

    style = ttk.Style(toplevel)
    style.configure("TButton", font = FONT_CONFIG, background = BUTTON_COLOR, padding = 10)
    style.configure("TLabel", font = FONT_CONFIG, padding = 10, background = BG_COLOR)

    manager = frameManager(toplevel)
    manager.new("AskEmail")
    manager.new("ChangePassword")
    manager.new("ChangeSuccess")

    emailErrLabel = ErrorLabel(manager.get("AskEmail"))
    emailErrLabel.place(relx = 0.5, rely = 0.325, anchor = "center")

    header = Label(manager.get("AskEmail"), text = "Password Reset", font = ("Arial", 16), bg = BG_COLOR, fg = FG_COLOR)
    header.place(relx = 0.5, rely = 0.03, anchor = "n")

    # (email entry)
    session = None
    def onEmailConfirm():
        if credential_validation.validate_email(emailVar.get()):
            nonlocal session
            manager.show("ChangePassword")
            session = PasswordResetSession(emailVar.get())
            session.sendVerificationCode()
        else:
            return emailErrLabel.raise_error("Please input your email properly and try again.")

    desc = Label(manager.get("AskEmail"), text = "We need to verify that it's you. Please enter the E - Mail to send the verification code to.", bg = BG_COLOR, fg = FG_COLOR, font = ("Arial", 12))
    desc.place(relx = 0.5, rely = 0.16, anchor = "n")
    desc.config(wraplength = "120m")

    email_lbl = lbl(manager.get("AskEmail"), text = "E-Mail", font = FONT_CONFIG)
    email_lbl.place(relx = 0.25, rely = 0.52, anchor = "e")

    email_entry = entryBox(manager.get("AskEmail"), font = FONT_CONFIG, textvariable = emailVar)
    email_entry.place(relx = 0.28, rely = 0.52, anchor = "w")

    email_confirm_btn = btn(manager.get("AskEmail"), command = onEmailConfirm, text = "Send Code")
    email_confirm_btn.place(relx = 0.5, rely = 0.9, anchor = "s")

    # verify code and change password frame
    verifyErrorLabel = ErrorLabel(manager.get("ChangePassword"))
    verifyErrorLabel.place(relx = 0.5, rely = 0.2, anchor = "center")

    def onSubmitNewPassword():
        verifyErrorLabel.hide()

        #verify some vars
        inputtedCode = verif_codeVar.get()
        inputtedPw = passwordVar.get()
        inputtedReEnterPw = passwordReEnterVar.get()

        vError = None
        if session.verificationCode != inputtedCode:
            vError = "Verification code is incorrect."
        if not credential_validation.validate_password(inputtedPw):
            vError = credential_validation.passwordCriteriaString
        if inputtedPw != inputtedReEnterPw:
            vError = "Passwords don't match."
        
        if vError:
            return verifyErrorLabel.raise_error(vError)
        
        #everything is validated from this point onwards, greenlight to change password so long as session actually exists
        if session:
            session.resetPassword(verif_codeVar.get(), inputtedPw)
            #show final screen
            manager.show("ChangeSuccess")

    header = Label(manager.get("ChangePassword"), text = "Change Password", font = ("Arial", 16), bg = BG_COLOR, fg = FG_COLOR)
    header.place(relx = 0.5, rely = 0.03, anchor = "n")

    start_y = 0.37
    y_inc = 0.3 - 0.15
    start_x = 0.42
    x_off = 0.02

    verif_code_lbl = lbl(manager.get("ChangePassword"), text = "Code", font = FONT_CONFIG)
    verif_code_lbl.place(relx = start_x, rely = start_y, anchor = "e")
    verif_code_entry = entryBox(manager.get("ChangePassword"), textvariable = verif_codeVar, font = FONT_CONFIG)
    verif_code_entry.place(relx = start_x + x_off, rely = start_y, anchor = "w")

    pwLbl = lbl(manager.get("ChangePassword"), font = FONT_CONFIG, text = "New Password")
    pwLbl.place(relx = start_x, rely = start_y + y_inc, anchor = "e")
    pwEntry = entryBox(manager.get("ChangePassword"), textvariable = passwordVar, font = FONT_CONFIG)
    pwEntry.place(relx = start_x + x_off, rely = start_y + y_inc, anchor = "w")

    againPwLbl = lbl(manager.get("ChangePassword"), font = FONT_CONFIG, text = "Confirm Password")
    againPwLbl.place(relx = start_x, rely = start_y + y_inc * 2, anchor = "e")
    againPwEntry = entryBox(manager.get("ChangePassword"), textvariable = passwordReEnterVar, font = FONT_CONFIG)
    againPwEntry.place(relx = start_x + x_off, rely = start_y + y_inc * 2, anchor = "w")

    submitNewPasswordButton = btn(manager.get("ChangePassword"), text = "CHANGE PASSWORD", command = onSubmitNewPassword)
    submitNewPasswordButton.place(relx = 0.5, rely = 0.98, anchor = "s")

    #final screen showing that password change was successful
    final_lbl = Label(manager.get("ChangeSuccess"), text = "Success! Your password has now been reset. You can close this window.", wraplength = "160m", fg = FG_COLOR, bg = BG_COLOR, font = FONT_CONFIG)
    final_lbl.place(relx = 0.5, rely = 0.5, anchor = "center")

    #main process of toplevel
    manager.show("AskEmail")
    
def login():
    loginErrorLabel.hide()

    username = textvariables.get("Login_Username").get()
    password = textvariables.get("Login_Password").get()
    
    vError = None
    #what site even requires a username to be non-numeric?
    if username == "":
        vError = "Username cannot be blank."
    if password == "":
        vError = "Password cannot be blank."
    
    if vError:
        return loginErrorLabel.raise_error(vError)
    
    success, err = credential_validation.validate_email(username)
    loginSuccess = False
    incorrectPassword = True
    credentialMatrix = {
        "customer": db.retrieve("customer"),
        "trainer": db.retrieve("trainer"),
        "manager": db.retrieve("manager")
    }

    loggedInUserType = None
    for key, vData in credentialMatrix.items():
        for data in vData:
            searchValue = success and data[9] or data[1]
            searchPassword = data[2]
            if (not success and username.lower() == searchValue.lower() or success and searchValue == username) and password == searchPassword:
                loginSuccess = True
                incorrectPassword = False
                loggedInUserType = key
                break
    
    if incorrectPassword:
        loginErrorLabel.raise_error("Username or password entered is incorrect. Please try again.")
    else:
        #menu procedure
        showMenu(loggedInUserType)

def updateCustomerControlPanelTV():
    customerControlPanelTV.flush()
    data = db.retrieve("customer")
    for credentials in data:
        customerControlPanelTV.insert(credentials[0], (credentials[1:]))

def updateTrainerControlPanelTV():
    trainerControlPanelTV.flush()
    data = db.retrieve("trainer")
    for credentials in data:
        trainerControlPanelTV.insert(credentials[0], (credentials[1:]))

def updateLessonControlPanelTV():
    lessonControlPanelTV.flush()
    data = db.retrieve("lesson")
    todayStr = datetime.today().strftime("%d/%m/%Y")
    for credentials in data:
        if not todayStr in credentials: continue
        lessonControlPanelTV.insert(credentials[0], (credentials[1:]))

def onUploadPfp():
    global signupPfpPath
    path = filedialog.askopenfilename()
    signupPfpPath = path
    imgKey = "PFPImage_" + str ( random.randint(1, 999999) )
    pfpButton.config(image = TkImagePool.open(path, imgKey, (120, 120) ) )

def takeFitnessTest(customerId):
    wx, wy = 680, 450
    widget = Toplevel()
    widget.geometry(f"{wx}x{wy}")
    widget.title("Fitness Test")

    mgr = frameManager(widget)
    mgr.new("Main")
    addLogoHeader(mgr.get("Main"))

    style = ttk.Style(widget)
    style.configure("TButton", font = FONT_CONFIG, background = BUTTON_COLOR, padding = 10)
    style.configure("TLabel", font = ("Arial", 20), padding = 10, background = BG_COLOR)

    weightVar = StringVar()
    heightVar = StringVar()
    runVar = StringVar()
    deadliftVar = StringVar()

    base_x = 0.56
    x_offset = 0.03
    base_y = 0.42
    y_increment = 0.11
    entry_font_cfg = ("Arial", 15)

    weightLbl = lbl(mgr.get("Main"), text = "Weight (KG)")
    weightLbl.place(relx = base_x, rely = base_y + y_increment * 0, anchor = "e")
    tooltip.new(weightLbl, "Weight must be a number between 20 and 800")
    entryBox(mgr.get("Main"), textvariable = weightVar, font = entry_font_cfg).place(relx = base_x + x_offset, rely = base_y + y_increment * 0, anchor = "w")

    heightLbl = lbl(mgr.get("Main"), text = "Height (cm)")
    heightLbl.place(relx = base_x, rely = base_y + y_increment * 1, anchor = "e")
    tooltip.new(heightLbl, "Height must be a number between 100 and 300")
    entryBox(mgr.get("Main"), textvariable = heightVar, font = entry_font_cfg).place(relx = base_x + x_offset, rely = base_y + y_increment * 1, anchor = "w")

    runLbl = lbl(mgr.get("Main"), text = "100K Run Time (minutes)")
    runLbl.place(relx = base_x, rely = base_y + y_increment * 2, anchor = "e")
    tooltip.new(runLbl, "100k Run Time must be a number in minutes and be bigger than 0")
    entryBox(mgr.get("Main"), textvariable = runVar, font = entry_font_cfg).place(relx = base_x + x_offset, rely = base_y + y_increment * 2, anchor = "w")

    deadliftLbl = lbl(mgr.get("Main"), text = "Max Deadlift (KG)")
    deadliftLbl.place(relx = base_x, rely = base_y + y_increment * 3, anchor = "e")
    tooltip.new(deadliftLbl, "Deadlift must be a number between 0 and 3000")
    entryBox(mgr.get("Main"), textvariable = deadliftVar, font = entry_font_cfg).place(relx = base_x + x_offset, rely = base_y + y_increment * 3, anchor = "w")

    def submitMetrics():
        def setState(lbl, state):
            if state == "err":
                lbl.config(foreground = "red")
            elif state == "default":
                lbl.config(foreground = "white")
        
        for lbl in [weightLbl, heightLbl, deadliftLbl, runLbl]:
            setState(lbl, "default")
        
        weight, height, run, deadlift = weightVar.get(), heightVar.get(), runVar.get(), deadliftVar.get()
        err = False
        if not util.isnumber(weight) or float(weight) < 20 or float(weight) > 800:
            setState(weightLbl, "err")
            err = True
        
        if not util.isnumber(height) or float(height) < 100 or float(height) > 300:
            setState(heightLbl, "err")
            err = True
        
        if not util.isnumber(run) or float(run) <= 0:
            setState(runLbl, "err")
            err = True
        
        if not util.isnumber(deadlift) or float(deadlift) < 0 or float(deadlift) > 3000:
            setState(deadliftLbl, "err")
            err = True
        
        if not err:
            #all is validated, submit to db
            db.create("customerMetrics", {
                "customerId": customerId,
                "weight": weight,
                "height": height,
                "run_time": run,
                "maxDeadlift": deadlift
            })

            messagebox.showinfo("Fitness Test", "Test completed successfully! You can now close this window.")
        
    btn(mgr.get("Main"), command = submitMetrics, text = "Submit Metrics").place(relx = 0.5, rely = 0.98, anchor = "s")

    mgr.show("Main")

def addCustomer():
    customerControlPanelErrorLabel.hide()

    username = textvariables.get("CustomerControlPanel_AddCustomerUsername").get()
    password = textvariables.get("CustomerControlPanel_AddCustomerPassword").get()
    firstName = textvariables.get("CustomerControlPanel_AddCustomerFirstName").get()
    lastName = textvariables.get("CustomerControlPanel_AddCustomerLastName").get()
    dob = textvariables.get("CustomerControlPanel_AddCustomerDOB").get()
    address = textvariables.get("CustomerControlPanel_AddCustomerAddress").get()
    telephone = textvariables.get("CustomerControlPanel_AddCustomerTelephone").get()
    postcode = textvariables.get("CustomerControlPanel_AddCustomerPostcode").get()
    email = textvariables.get("CustomerControlPanel_AddCustomerEmail").get()

    #this mess needs converted to an iterative solution at some point
    success, err = None, None
    success, err = credential_validation.validate_username(username)
    #also ensure they aren't signing up with a username which is in use
    for data in db.retrieve("customer"):
        if data[1].lower() == username.lower():
            success, err = False, "Username is already in use. Please try something else."
            break
    
    if success:
        success, err = credential_validation.validate_password(password)
    if success:
        success, err = credential_validation.validate_name(firstName)
    if success:
        success, err = credential_validation.validate_name(lastName)
    if success:
        success, err = credential_validation.validate_address(address)
    if success:
        success, err = credential_validation.validate_telephone(telephone)
    if success:
        success, err = credential_validation.validate_postcode(postcode)
    if success:
        success, err = credential_validation.validate_email(email)

    if not success and err:
        return messagebox.showerror("Add Customer Error", err)

    #all data validated past this point

    pfpData = None
    if signupPfpPath:
        with open(signupPfpPath, "rb") as file:
            pfpData = file.read()

    print("pfp DONE")

    customerId = db.generateId("customer")
    db.create("customer", {
        "customerId": customerId,
        "username": username,
        "password": password,
        "firstName": firstName,
        "lastName": lastName,
        "postcode": postcode,
        "address": address,
        "telephone": telephone,
        "dateOfBirth": dob,
        "email": email,
        "profilePicture": pfpData or "",
        "pendingVerificationCode": ""
    })

    updateCustomerControlPanelTV()

    s = f"""
        Hey {firstName},

        Welcome to the Elite Fitness club.

        Here's a quick list of our available classes:
    """

    for classData in db.retrieve("lesson"):
        pass
    

    emailUtil.send_email(email, "Welcome to the Elite Fitness Club!", s)
    response = messagebox.askyesno("Create Success", "Customer successfully added to database! Would you like to take a fitness test?")

    if response == YES:
        takeFitnessTest(customerId)

def updateCustomer(isContextMenu = False):
    inputtedUsername = None
    if isContextMenu:
        inputtedUsername = customerControlPanelTV.treeview.item(customerControlPanelTV.treeview.focus())["values"][0]
    else:
        inputtedUsername = simpledialog.askstring("Update Request", "Please enter the username of the customer which you wish to update.")
    print(inputtedUsername)

    customerId = None
    for data in db.retrieve("customer"):
        if data[1].lower() == inputtedUsername.lower():
            customerId = int(data[0])
            break
    
    if customerId == None: return
    #init the toplevel for different buttons

    wx, wy = 630, 380
    widget = Toplevel()
    widget.geometry(f"{wx}x{wy}")
    widget.title("Update Customer Details")

    style = ttk.Style(widget)
    style.configure("TButton", font = FONT_CONFIG, background = BUTTON_COLOR, padding = 10)
    style.configure("TLabel", font = FONT_CONFIG, padding = 10, background = BG_COLOR)
    
    #create frame
    frame = Frame(widget, bg = BG_COLOR, width = wx, height = wy)
    frame.grid(row = 0, column = 0, sticky = "news")

    base_x = 0.5
    base_y = 0.04
    y_increment = 0.35
    btn_width = 25

    def updateAddress():
        newAddress = simpledialog.askstring("Update Address", "Please enter a new address")
        success, err = credential_validation.validate_address(newAddress)
        if not success and err:
            shouldRetry = messagebox.askretrycancel("Update Address Error", err)
            if shouldRetry: return updateAddress()
        
        db.update("customer", customerId, "address", newAddress)
        updateCustomerControlPanelTV()
        messagebox.showinfo("Update Success", "Address updated successfully!")

    def updatePostcode():
        newPostcode = simpledialog.askstring("Update Postcode", "Please enter a new postcode")
        success, err = credential_validation.validate_postcode(newPostcode)
        if not success and err:
            shouldRetry = messagebox.askretrycancel("Update Postcode Error", err)
            if shouldRetry: return updatePostcode()
        
        db.update("customer", customerId, "postcode", newPostcode)
        updateCustomerControlPanelTV()
        messagebox.showinfo("Update Success", "Postcode updated successfully!")

    def updateTelephone():
        newTelephone = simpledialog.askstring("Update Telephone", "Please enter a new telephone")
        success, err = credential_validation.validate_telephone(newTelephone)
        if not success and err:
            shouldRetry = messagebox.askretrycancel("Update Telephone Error", err)
            if shouldRetry: return updateTelephone()
        
        db.update("customer", customerId, "telephone", newTelephone)
        updateCustomerControlPanelTV()
        messagebox.showinfo("Update Success", "Telephone updated successfully!")
    
    updateAddressButton = btn(frame, text = "UPDATE ADDRESS", command = updateAddress, width = btn_width)
    updateAddressButton.place(relx = base_x, rely = base_y + y_increment * 0, anchor = N)
    tooltip.new(updateAddressButton, "Update the user's address")

    updatePostcodeButton = btn(frame, text = "UPDATE POSTCODE", command = updatePostcode, width = btn_width)
    updatePostcodeButton.place(relx = base_x, rely = base_y + y_increment * 1, anchor = N)
    tooltip.new(updatePostcodeButton, "Update the user's postcode")

    updateTelephoneButton = btn(frame, text = "UPDATE TELEPHONE", command = updateTelephone, width = btn_width)
    updateTelephoneButton.place(relx = base_x, rely = base_y + y_increment * 2, anchor = N)
    tooltip.new(updateTelephoneButton, "Update the user's telephone")

def deleteCustomer(isContextMenu = False):
    if not isContextMenu:
        username = simpledialog.askstring("Delete Customer", "Please input the username of the customer who you want to remove from the database.")
    elif len(customerControlPanelTV.treeview.item(customerControlPanelTV.treeview.focus())["values"]) > 0:
        username = customerControlPanelTV.treeview.item(customerControlPanelTV.treeview.focus())["values"][0]
    
    customerId = None
    for data in db.retrieve("customer"):
        if data[1].lower() == username.lower():
            customerId = int(data[0])
            break
    
    if customerId == None: return
    
    if messagebox.askyesno("Delete Customer", "Are you sure you want to delete this customer? This cannot be undone.") == YES:
        db.delete("customer", customerId)
        db.delete("customerMetrics", customerId)
        updateCustomerControlPanelTV()#

def addTrainer():
    username = textvariables.get("TrainerControlPanel_AddTrainerUsername").get()
    password = textvariables.get("TrainerControlPanel_AddTrainerPassword").get()
    firstName = textvariables.get("TrainerControlPanel_AddTrainerFirstName").get()
    lastName = textvariables.get("TrainerControlPanel_AddTrainerLastName").get()
    dob = textvariables.get("TrainerControlPanel_AddTrainerDOB").get()
    address = textvariables.get("TrainerControlPanel_AddTrainerAddress").get()
    telephone = textvariables.get("TrainerControlPanel_AddTrainerTelephone").get()
    postcode = textvariables.get("TrainerControlPanel_AddTrainerPostcode").get()
    email = textvariables.get("TrainerControlPanel_AddTrainerEmail").get()

    #this mess needs converted to an iterative solution at some point
    success, err = None, None
    success, err = credential_validation.validate_username(username)
    #also ensure they aren't signing up with a username which is in use
    for data in db.retrieve("trainer"):
        if data[1].lower() == username.lower():
            success, err = False, "Username is already in use. Please try something else."
            break
    
    if success:
        success, err = credential_validation.validate_password(password)
    if success:
        success, err = credential_validation.validate_name(firstName)
    if success:
        success, err = credential_validation.validate_name(lastName)
    if success:
        success, err = credential_validation.validate_address(address)
    if success:
        success, err = credential_validation.validate_telephone(telephone)
    if success:
        success, err = credential_validation.validate_postcode(postcode)
    if success:
        success, err = credential_validation.validate_email(email)

    if not success and err:
        return messagebox.showerror("Add Trainer Error", err)

    #all data validated past this point

    pfpData = None
    if signupPfpPath:
        with open(signupPfpPath, "rb") as file:
            pfpData = file.read()

    print("pfp DONE")

    trainerId = db.generateId("trainer")
    db.create("trainer", {
        "trainerId": trainerId,
        "username": username,
        "password": password,
        "firstName": firstName,
        "lastName": lastName,
        "postcode": postcode,
        "address": address,
        "telephone": telephone,
        "dateOfBirth": dob,
        "email": email,
        "profilePicture": pfpData or "",
        "pendingVerificationCode": ""
    })

    updateTrainerControlPanelTV()
    response = messagebox.askyesno("Create Success", "Trainer successfully added to database!")

def updateTrainer(isContextMenu = False):
    inputtedUsername = None
    if isContextMenu:
        inputtedUsername = trainerControlPanelTV.treeview.item(trainerControlPanelTV.treeview.focus())["values"][0]
    else:
        inputtedUsername = simpledialog.askstring("Update Request", "Please enter the username of the trainer which you wish to update.")
    print(inputtedUsername)

    trainerId = None
    for data in db.retrieve("trainer"):
        if data[1].lower() == inputtedUsername.lower():
            trainerId = int(data[0])
            break
    
    if trainerId == None: return
    #init the toplevel for different buttons

    wx, wy = 630, 380
    widget = Toplevel()
    widget.geometry(f"{wx}x{wy}")
    widget.title("Update Trainer Details")

    style = ttk.Style(widget)
    style.configure("TButton", font = FONT_CONFIG, background = BUTTON_COLOR, padding = 10)
    style.configure("TLabel", font = FONT_CONFIG, padding = 10, background = BG_COLOR)
    
    #create frame
    frame = Frame(widget, bg = BG_COLOR, width = wx, height = wy)
    frame.grid(row = 0, column = 0, sticky = "news")

    base_x = 0.5
    base_y = 0.04
    y_increment = 0.35
    btn_width = 25

    def updateAddress():
        newAddress = simpledialog.askstring("Update Address", "Please enter a new address")
        success, err = credential_validation.validate_address(newAddress)
        if not success and err:
            shouldRetry = messagebox.askretrycancel("Update Address Error", err)
            if shouldRetry: return updateAddress()
        
        db.update("trainer", trainerId, "address", newAddress)
        updateTrainerControlPanelTV()
        messagebox.showinfo("Update Success", "Address updated successfully!")

    def updatePostcode():
        newPostcode = simpledialog.askstring("Update Postcode", "Please enter a new postcode")
        success, err = credential_validation.validate_postcode(newPostcode)
        if not success and err:
            shouldRetry = messagebox.askretrycancel("Update Postcode Error", err)
            if shouldRetry: return updatePostcode()
        
        db.update("trainer", trainerId, "postcode", newPostcode)
        updateTrainerControlPanelTV()
        messagebox.showinfo("Update Success", "Postcode updated successfully!")

    def updateTelephone():
        newTelephone = simpledialog.askstring("Update Telephone", "Please enter a new telephone")
        success, err = credential_validation.validate_telephone(newTelephone)
        if not success and err:
            shouldRetry = messagebox.askretrycancel("Update Telephone Error", err)
            if shouldRetry: return updateTelephone()
        
        db.update("trainer", trainerId, "telephone", newTelephone)
        updateTrainerControlPanelTV()
        messagebox.showinfo("Update Success", "Telephone updated successfully!")
    
    updateAddressButton = btn(frame, text = "UPDATE ADDRESS", command = updateAddress, width = btn_width)
    updateAddressButton.place(relx = base_x, rely = base_y + y_increment * 0, anchor = N)
    tooltip.new(updateAddressButton, "Update the user's address")

    updatePostcodeButton = btn(frame, text = "UPDATE POSTCODE", command = updatePostcode, width = btn_width)
    updatePostcodeButton.place(relx = base_x, rely = base_y + y_increment * 1, anchor = N)
    tooltip.new(updatePostcodeButton, "Update the user's postcode")

    updateTelephoneButton = btn(frame, text = "UPDATE TELEPHONE", command = updateTelephone, width = btn_width)
    updateTelephoneButton.place(relx = base_x, rely = base_y + y_increment * 2, anchor = N)
    tooltip.new(updateTelephoneButton, "Update the user's telephone")

def deleteTrainer(isContextMenu = False):
    if not isContextMenu:
        username = simpledialog.askstring("Delete Trainer", "Please input the username of the trainer who you want to remove from the database.")
    elif len(trainerControlPanelTV.treeview.item(trainerControlPanelTV.treeview.focus())["values"]) > 0:
        username = trainerControlPanelTV.treeview.item(trainerControlPanelTV.treeview.focus())["values"][0]
    
    trainerId = None
    for data in db.retrieve("trainer"):
        if data[1].lower() == username.lower():
            trainerId = int(data[0])
            break
    
    if trainerId == None: return
    
    if messagebox.askyesno("Delete Trainer", "Are you sure you want to delete this trainer? This cannot be undone.") == YES:
        db.delete("trainer", trainerId)
        db.delete("trainerMetrics", trainerId)
        updateTrainerControlPanelTV()

def addLesson():
    global lessonTypeOptions

    lessonType = textvariables.get("LessonControlPanel_LessonType").get()
    duration = textvariables.get("LessonControlPanel_Duration").get()
    date = textvariables.get("LessonControlPanel_Date").get()
    locationId = textvariables.get("LessonControlPanel_LocationId").get()
    trainerId = textvariables.get("LessonControlPanel_TrainerId").get()
    maxPeople = textvariables.get("LessonControlPanel_MaxPeople").get()

    err = ""

    if not util.isnumber(duration) or float(duration) < 0 or float(duration) > 3:
        err = "The lesson must not be longer than 3 hours and the number inputted must be greater than 0."
    
    validLocation = False
    records = db.retrieve("location")
    for record in records:
        if record[0] == int(locationId):
            validLocation = True
            break
    
    validTrainer = False
    trainerRecords = db.retrieve("trainer")
    for record in trainerRecords:
        if record[0] == int(trainerId):
            validTrainer = True
            break
    
    if not validLocation:
        err = "Please input a valid location ID."

    if not validTrainer:
        err = "Please input a valid trainer ID."
    
    if err != "":
        return messagebox.showerror("Add Lesson Error", err)

    #all data validated past this point

    lessonId = db.generateId("lesson")
    db.create("lesson", {
        "lessonId": db.generateId("lesson"),
        "trainerId": trainerId,
        "lessonType": lessonType,
        "duration": duration,
        "date": date,
        "locationId": locationId,
        "maxPeople": maxPeople,
        "currentPeople": 0
    })

    updateLessonControlPanelTV()
    updateLessonCalendar()
    response = messagebox.showinfo("Create Success", "Lesson successfully added to database!")

def updateLesson(isContextMenu = False):
    inputtedUsername = None
    if isContextMenu:
        inputtedUsername = lessonControlPanelTV.treeview.item(lessonControlPanelTV.treeview.focus())["text"]
    else:
        inputtedUsername = simpledialog.askstring("Update Request", "Please enter the ID of the lesson which you wish to update.")

    lessonId = type(inputtedUsername) == "string" and int(inputtedUsername) or inputtedUsername
    
    if lessonId == None: return
    #init the toplevel for different buttons

    wx, wy = 630, 380
    widget = Toplevel()
    widget.geometry(f"{wx}x{wy}")
    widget.title("Update Lesson Details")

    style = ttk.Style(widget)
    style.configure("TButton", font = FONT_CONFIG, background = BUTTON_COLOR, padding = 10)
    style.configure("TLabel", font = FONT_CONFIG, padding = 10, background = BG_COLOR)
    
    #create frame
    frame = Frame(widget, bg = BG_COLOR, width = wx, height = wy)
    frame.grid(row = 0, column = 0, sticky = "news")

    base_x = 0.5
    base_y = 0.04
    y_increment = 0.35
    btn_width = 25

    def updateAddress():
        newAddress = simpledialog.askstring("Update Duration", "Please enter a new duration")
        if not util.isnumber(newAddress) or int(newAddress) < 0 or int(newAddress) > 3:
            shouldRetry = messagebox.askretrycancel("Update Duration Error", "Duration must be a number between 0 and 3")
            if shouldRetry: return updateAddress()
        
        db.update("lesson", lessonId, "duration", newAddress)
        updateLessonControlPanelTV()
        messagebox.showinfo("Update Success", "Duration updated successfully!")

    def updatePostcode():
        newPostcode = simpledialog.askstring("Update Max people", "Please enter a maximum number of people")
        if not util.isnumber(newPostcode) or int(newPostcode) < 0:
            shouldRetry = messagebox.askretrycancel("Update Max People Error", "Max People must be a number greater than 0")
            if shouldRetry: return updatePostcode()
        
        db.update("lesson", lessonId, "maxPeople", newPostcode)
        updateLessonControlPanelTV()
        messagebox.showinfo("Update Success", "Max People updated successfully!")

    def updateTelephone():
        newTelephone = simpledialog.askstring("Update Lesson Type", "Please enter a new Lesson Type")
        if not newTelephone in lessonTypeOptions:
            shouldRetry = messagebox.askretrycancel("Update Lesson Type Error", "Lesson Type must be one of the specific class types")
            if shouldRetry: return updateTelephone()
        
        db.update("lesson", lessonId, "lessonType", newTelephone)
        updateLessonControlPanelTV()
        messagebox.showinfo("Update Success", "Lesson Type updated successfully!")
    
    updateAddressButton = btn(frame, text = "UPDATE DURATION", command = updateAddress, width = btn_width)
    updateAddressButton.place(relx = base_x, rely = base_y + y_increment * 0, anchor = N)
    tooltip.new(updateAddressButton, "Update the duration")

    updatePostcodeButton = btn(frame, text = "UPDATE CAPACITY", command = updatePostcode, width = btn_width)
    updatePostcodeButton.place(relx = base_x, rely = base_y + y_increment * 1, anchor = N)
    tooltip.new(updatePostcodeButton, "Update the max people allowed in the lesson")

    updateTelephoneButton = btn(frame, text = "UPDATE LESSON TYPE", command = updateTelephone, width = btn_width)
    updateTelephoneButton.place(relx = base_x, rely = base_y + y_increment * 2, anchor = N)
    tooltip.new(updateTelephoneButton, "Update the lesson type")

def deleteLesson(isContextMenu = False):
    if not isContextMenu:
        username = simpledialog.askstring("Delete Lesson", "Please input the ID of the lesson who you want to remove from the database.")
    elif len(lessonControlPanelTV.treeview.item(lessonControlPanelTV.treeview.focus())["values"]) > 0:
        username = lessonControlPanelTV.treeview.item(lessonControlPanelTV.treeview.focus())["text"]
    
    username = type(username) == "string" and int(username) or username
    
    lessonId = username
    
    if lessonId == None: return
    
    if messagebox.askyesno("Delete Lesson", "Are you sure you want to delete this lesson? This cannot be undone.") == YES:
        db.delete("lesson", lessonId)
        updateLessonControlPanelTV()

def addLocation():
    global locationTypeOptions

    locationType = textvariables.get("LocationControlPanel_LocationType").get()
    duration = textvariables.get("LocationControlPanel_Duration").get()
    date = textvariables.get("LocationControlPanel_Date").get()
    locationId = textvariables.get("LocationControlPanel_LocationId").get()
    trainerId = textvariables.get("LocationControlPanel_TrainerId").get()
    maxPeople = textvariables.get("LocationControlPanel_MaxPeople").get()

    err = ""

    if not util.isnumber(duration) or float(duration) < 0 or float(duration) > 3:
        err = "The location must not be longer than 3 hours and the number inputted must be greater than 0."
    
    validLocation = False
    records = db.retrieve("location")
    for record in records:
        if record[0] == int(locationId):
            validLocation = True
            break
    
    validTrainer = False
    trainerRecords = db.retrieve("trainer")
    for record in trainerRecords:
        if record[0] == int(trainerId):
            validTrainer = True
            break
    
    if not validLocation:
        err = "Please input a valid location ID."

    if not validTrainer:
        err = "Please input a valid trainer ID."
    
    if err != "":
        return messagebox.showerror("Add Location Error", err)

    #all data validated past this point

    locationId = db.generateId("location")
    db.create("location", {
        "locationId": db.generateId("location"),
        "trainerId": trainerId,
        "locationType": locationType,
        "duration": duration,
        "date": date,
        "locationId": locationId,
        "maxPeople": maxPeople,
        "currentPeople": 0
    })

    updateLocationControlPanelTV()
    updateLocationCalendar()
    response = messagebox.showinfo("Create Success", "Location successfully added to database!")

def updateLocation(isContextMenu = False):
    inputtedUsername = None
    if isContextMenu:
        inputtedUsername = locationControlPanelTV.treeview.item(locationControlPanelTV.treeview.focus())["text"]
    else:
        inputtedUsername = simpledialog.askstring("Update Request", "Please enter the ID of the location which you wish to update.")

    locationId = type(inputtedUsername) == "string" and int(inputtedUsername) or inputtedUsername
    
    if locationId == None: return
    #init the toplevel for different buttons

    wx, wy = 630, 380
    widget = Toplevel()
    widget.geometry(f"{wx}x{wy}")
    widget.title("Update Location Details")

    style = ttk.Style(widget)
    style.configure("TButton", font = FONT_CONFIG, background = BUTTON_COLOR, padding = 10)
    style.configure("TLabel", font = FONT_CONFIG, padding = 10, background = BG_COLOR)
    
    #create frame
    frame = Frame(widget, bg = BG_COLOR, width = wx, height = wy)
    frame.grid(row = 0, column = 0, sticky = "news")

    base_x = 0.5
    base_y = 0.04
    y_increment = 0.35
    btn_width = 25

    def updateAddress():
        newAddress = simpledialog.askstring("Update Duration", "Please enter a new duration")
        if not util.isnumber(newAddress) or int(newAddress) < 0 or int(newAddress) > 3:
            shouldRetry = messagebox.askretrycancel("Update Duration Error", "Duration must be a number between 0 and 3")
            if shouldRetry: return updateAddress()
        
        db.update("location", locationId, "duration", newAddress)
        updateLocationControlPanelTV()
        messagebox.showinfo("Update Success", "Duration updated successfully!")

    def updatePostcode():
        newPostcode = simpledialog.askstring("Update Max people", "Please enter a maximum number of people")
        if not util.isnumber(newPostcode) or int(newPostcode) < 0:
            shouldRetry = messagebox.askretrycancel("Update Max People Error", "Max People must be a number greater than 0")
            if shouldRetry: return updatePostcode()
        
        db.update("location", locationId, "maxPeople", newPostcode)
        updateLocationControlPanelTV()
        messagebox.showinfo("Update Success", "Max People updated successfully!")

    def updateTelephone():
        newTelephone = simpledialog.askstring("Update Location Type", "Please enter a new Location Type")
        if not newTelephone in locationTypeOptions:
            shouldRetry = messagebox.askretrycancel("Update Location Type Error", "Location Type must be one of the specific class types")
            if shouldRetry: return updateTelephone()
        
        db.update("location", locationId, "locationType", newTelephone)
        updateLocationControlPanelTV()
        messagebox.showinfo("Update Success", "Location Type updated successfully!")
    
    updateAddressButton = btn(frame, text = "UPDATE DURATION", command = updateAddress, width = btn_width)
    updateAddressButton.place(relx = base_x, rely = base_y + y_increment * 0, anchor = N)
    tooltip.new(updateAddressButton, "Update the duration")

    updatePostcodeButton = btn(frame, text = "UPDATE CAPACITY", command = updatePostcode, width = btn_width)
    updatePostcodeButton.place(relx = base_x, rely = base_y + y_increment * 1, anchor = N)
    tooltip.new(updatePostcodeButton, "Update the max people allowed in the location")

    updateTelephoneButton = btn(frame, text = "UPDATE LESSON TYPE", command = updateTelephone, width = btn_width)
    updateTelephoneButton.place(relx = base_x, rely = base_y + y_increment * 2, anchor = N)
    tooltip.new(updateTelephoneButton, "Update the location type")

def deleteLocation(isContextMenu = False):
    if not isContextMenu:
        username = simpledialog.askstring("Delete Location", "Please input the ID of the location who you want to remove from the database.")
    elif len(locationControlPanelTV.treeview.item(locationControlPanelTV.treeview.focus())["values"]) > 0:
        username = locationControlPanelTV.treeview.item(locationControlPanelTV.treeview.focus())["text"]
    
    username = type(username) == "string" and int(username) or username
    
    locationId = username
    
    if locationId == None: return
    
    if messagebox.askyesno("Delete Location", "Are you sure you want to delete this location? This cannot be undone.") == YES:
        db.delete("location", locationId)
        updateLocationControlPanelTV()



def onTreeviewPopup(tv, popup, event):
    try:
        rowItem = tv.treeview.identify_row(event.y)
        popup.selection = tv.treeview.set(rowItem)
        tv.treeview.selection_set(rowItem)
        tv.treeview.focus(rowItem)
        popup.post(event.x_root, event.y_root)
    finally:
        tv.treeview.grab_release()

#login frame
fRoot.new("Login")

#header img
addLogoHeader(fRoot.get("Login"))

loginErrorLabel = ErrorLabel(fRoot.get("Login"))
loginErrorLabel.place(relx = 0.5, rely = 0.3, anchor = "center")

#digital clock
loginClock = clock(fRoot.get("Login"))
loginClock.place(relx = 0.5, rely = 0.18, anchor = "n")

usernameLoginLabel = lbl(fRoot.get("Login"), text = "Username", font = FONT_CONFIG)
tooltip.new(usernameLoginLabel, "Enter your username in this field")
usernameLoginLabel.place(relx = 0.3, rely = 0.4, anchor = "e")
usernameLoginEntry = entryBox(fRoot.get("Login"), textvariable = textvariables.get("Login_Username"), font = FONT_CONFIG)
usernameLoginEntry.place(relx = 0.34, rely = 0.4, anchor = "w")

passwordLoginLabel = lbl(fRoot.get("Login"), text = "Password")
tooltip.new(passwordLoginLabel, "Enter your password in this field")
passwordLoginLabel.place(relx = 0.3, rely = 0.5, anchor = "e")
passwordLoginEntry = entryBox(fRoot.get("Login"), textvariable = textvariables.get("Login_Password"), font = FONT_CONFIG, show = "*")
passwordLoginEntry.place(relx = 0.34, rely = 0.5, anchor = "w")

loginButton = btn(fRoot.get("Login"), text = "Login", width = 18, command = login)
tooltip.new(loginButton, "Click here to login")
loginButton.place(relx = 0.5, rely = 0.65, anchor = "center")

forgotPasswordButton = btn(fRoot.get("Login"), text = "Forgot Password?", width = 18, command = onPasswordReset)
forgotPasswordButton.place(relx = 0.5, rely = 0.74, anchor = "center")

#social media buttons
TkImagePool.open("ig_logo.png", "IG_Logo", (100, 100))
TkImagePool.open("fb_logo.png", "FB_Logo", (100, 100))
button_offset = 0.05
button_y = 0.97
igButton = Button(fRoot.get("Login"), image = TkImagePool.get("IG_Logo"), bg = BG_COLOR, borderwidth = 0, activebackground = BG_ACCENT_COLOR, command = partial(webbrowser.open_new_tab, "https://instagram.com/teamelitelisburn?igshid=1ch87cdsy7no0"))
igButton.place(relx = 0.5 - button_offset, rely = button_y, anchor = SE)
tooltip.new(igButton, "Follow us on Instagram")

fbButton = Button(fRoot.get("Login"), image = TkImagePool.get("FB_Logo"), bg = BG_COLOR, borderwidth = 0, activebackground = BG_ACCENT_COLOR, command = partial(webbrowser.open_new_tab, "https://www.facebook.com/Elite-Health-and-Fitness-Lisburn-678912068907016/"))
fbButton.place(relx = 0.5 + button_offset, rely = button_y, anchor = SW)
tooltip.new(fbButton, "Follow us on Facebook")

#general menu frame
#todo: create sidebar object with bindings from buttons to frames?
fRoot.new("Menu_Base")
addLogoHeader(fRoot.get("Menu_Base"), 0.076)

#menu sidebar
#add all buttons by default, shift around based on levels of access for each user
sidebar = DynamicSidebar(fRoot, "Menu_Sidebar")
sidebar.addButton(os.path.join("menu_icons", "new_user_icon.png"), "CustomerControlPanel")
sidebar.linkButton("CustomerControlPanel", "CustomerControlPanel")

#customer control panel frame
fRoot.new("CustomerControlPanel")
addLogoHeader(fRoot.get("CustomerControlPanel"), 0.076)
sidebar.linkButton("CustomerControlPanel", "CustomerControlPanel")
customerControlPanelErrorLabel = ErrorLabel(fRoot.get("CustomerControlPanel"))
customerControlPanelErrorLabel.config(wraplength = "90m")
customerControlPanelErrorLabel.place(relx = 0.03, rely = 0.01, anchor = NW)

textvariables.create("CustomerControlPanel_AddCustomerUsername", StringVar())
textvariables.create("CustomerControlPanel_AddCustomerPassword", StringVar())
textvariables.create("CustomerControlPanel_AddCustomerFirstName", StringVar())
textvariables.create("CustomerControlPanel_AddCustomerLastName", StringVar())
textvariables.create("CustomerControlPanel_AddCustomerDOB", StringVar())
textvariables.create("CustomerControlPanel_AddCustomerAddress", StringVar())
textvariables.create("CustomerControlPanel_AddCustomerTelephone", StringVar())
textvariables.create("CustomerControlPanel_AddCustomerPostcode", StringVar())
textvariables.create("CustomerControlPanel_AddCustomerEmail", StringVar())

start_x = 0.3
start_y = 0.2
y_increment = 0.06
button_x_offset = 0.02
font_cfg = ("Arial", 15)

usernameLabel = lbl(fRoot.get("CustomerControlPanel"), text = "Username", font = font_cfg)
usernameLabel.place(relx = start_x, rely = start_y, anchor = "e")
usernameEntry = entryBox(fRoot.get("CustomerControlPanel"), font = font_cfg, textvariable = textvariables.get("CustomerControlPanel_AddCustomerUsername"))
usernameEntry.place(relx = start_x + button_x_offset, rely = start_y, anchor = "w")

passwordLabel = lbl(fRoot.get("CustomerControlPanel"), text = "Password", font = font_cfg)
passwordLabel.place(relx = start_x, rely = start_y + y_increment * 1, anchor = "e")
passwordEntry = entryBox(fRoot.get("CustomerControlPanel"), font = font_cfg, show = "*", textvariable = textvariables.get("CustomerControlPanel_AddCustomerPassword"))
passwordEntry.place(relx = start_x + button_x_offset, rely = start_y + y_increment * 1, anchor = "w")

firstNameLabel = lbl(fRoot.get("CustomerControlPanel"), text = "First Name", font = font_cfg)
firstNameLabel.place(relx = start_x, rely = start_y + y_increment * 2, anchor = "e")
firstNameEntry = entryBox(fRoot.get("CustomerControlPanel"), font = font_cfg, textvariable = textvariables.get("CustomerControlPanel_AddCustomerFirstName"))
firstNameEntry.place(relx = start_x + button_x_offset, rely = start_y + y_increment * 2, anchor = "w")

lastNameLabel = lbl(fRoot.get("CustomerControlPanel"), text = "Last Name", font = font_cfg)
lastNameLabel.place(relx = start_x, rely = start_y + y_increment * 3, anchor = "e")
lastNameEntry = entryBox(fRoot.get("CustomerControlPanel"), font = font_cfg, textvariable = textvariables.get("CustomerControlPanel_AddCustomerLastName"))
lastNameEntry.place(relx = start_x + button_x_offset, rely = start_y + y_increment * 3, anchor = "w")

dobLabel = lbl(fRoot.get("CustomerControlPanel"), text = "Birth Date", font = font_cfg)
dobLabel.place(relx = start_x, rely = start_y + y_increment * 4, anchor = "e")
dobEntry = DateEntry(fRoot.get("CustomerControlPanel"), font = font_cfg, textvariable = textvariables.get("CustomerControlPanel_AddCustomerDOB"))
dobEntry.place(relx = start_x + button_x_offset, rely = start_y + y_increment * 4, anchor = "w")

addressLabel = lbl(fRoot.get("CustomerControlPanel"), text = "Address", font = font_cfg)
addressLabel.place(relx = start_x, rely = start_y + y_increment * 5, anchor = "e")
addressEntry = entryBox(fRoot.get("CustomerControlPanel"), font = font_cfg, textvariable = textvariables.get("CustomerControlPanel_AddCustomerAddress"))
addressEntry.place(relx = start_x + button_x_offset, rely = start_y + y_increment * 5, anchor = "w")

telephoneLabel = lbl(fRoot.get("CustomerControlPanel"), text = "Telephone", font = font_cfg)
telephoneLabel.place(relx = start_x, rely = start_y + y_increment * 6, anchor = "e")
telephoneEntry = entryBox(fRoot.get("CustomerControlPanel"), font = font_cfg, textvariable = textvariables.get("CustomerControlPanel_AddCustomerTelephone"))
telephoneEntry.place(relx = start_x + button_x_offset, rely = start_y + y_increment * 6, anchor = "w")

postcodeLabel = lbl(fRoot.get("CustomerControlPanel"), text = "Postcode", font = font_cfg)
postcodeLabel.place(relx = start_x, rely = start_y + y_increment * 7, anchor = "e")
postcodeEntry = entryBox(fRoot.get("CustomerControlPanel"), font = font_cfg, textvariable = textvariables.get("CustomerControlPanel_AddCustomerPostcode"))
postcodeEntry.place(relx = start_x + button_x_offset, rely = start_y + y_increment * 7, anchor = "w")

emailLabel = lbl(fRoot.get("CustomerControlPanel"), text = "E-Mail", font = font_cfg)
emailLabel.place(relx = start_x, rely = start_y + y_increment * 8, anchor = "e")
emailEntry = entryBox(fRoot.get("CustomerControlPanel"), font = font_cfg, textvariable = textvariables.get("CustomerControlPanel_AddCustomerEmail"))
emailEntry.place(relx = start_x + button_x_offset, rely = start_y + y_increment * 8, anchor = "w")

TkImagePool.open("upload_pfp_img.png", "UploadPFP_Icon", (120, 120) )
pfpLabel = lbl(fRoot.get("CustomerControlPanel"), text = ("Upload Profile Picture (Optional)"), font = ("Arial", 14))
pfpLabel.place(relx = 0.83, rely = 0.22, anchor = "center")
pfpButton = Button(fRoot.get("CustomerControlPanel"), command = onUploadPfp, image = TkImagePool.get("UploadPFP_Icon"), activebackground = BG_ACCENT_COLOR, bg = BG_ACCENT_COLOR, borderwidth = 0)
pfpButton.place(relx = 0.83, rely = 0.235, anchor = "n")

#treeview widget
customerControlPanelTVPopup = Menu(fRoot.get("CustomerControlPanel"), tearoff = 0)
customerControlPanelTVPopup.add_command(label = "Update", command = partial(updateCustomer, True))
customerControlPanelTVPopup.add_separator()
customerControlPanelTVPopup.add_command(label = "Delete", command = partial(deleteCustomer, True))

customerControlPanelTV = TV(fRoot.get("CustomerControlPanel"), "ID", "Username", "Password", "First Name", "Last Name", "Postcode", "Address", "Telephone", "DOB", "E-Mail")
customerControlPanelTV.treeview.place(relx = 0.57, rely = 0.98, anchor = "s")
customerControlPanelTV.treeview.bind("<Button-3>", partial(onTreeviewPopup, customerControlPanelTV, customerControlPanelTVPopup))

#buttons for customer control panel
start_x = 0.98
start_y = 0.45
y_increment = 0.105
btn_width = 14

addCustomerButton = btn(fRoot.get("CustomerControlPanel"), text = "Add Customer", width = btn_width, command = addCustomer)
addCustomerButton.place(relx = start_x, rely = start_y, anchor = "e")

updateCustomerButton = btn(fRoot.get("CustomerControlPanel"), text = "Update Customer", width = btn_width, command = updateCustomer)
updateCustomerButton.place(relx = start_x, rely = start_y + y_increment * 1, anchor = "e")

deleteCustomerButton = btn(fRoot.get("CustomerControlPanel"), text = "Delete Customer", width = btn_width, command = deleteCustomer)
deleteCustomerButton.place(relx = start_x, rely = start_y + y_increment * 2, anchor = "e")

#ADD TRAINER FRAME
fRoot.new("TrainerControlPanel")
sidebar.addButton(os.path.join("menu_icons", "new_trainer_icon.png"), "TrainerControlPanel")
sidebar.linkButton("TrainerControlPanel", "TrainerControlPanel")
addLogoHeader(fRoot.get("TrainerControlPanel"), 0.076)

textvariables.create("TrainerControlPanel_AddTrainerUsername", StringVar())
textvariables.create("TrainerControlPanel_AddTrainerPassword", StringVar())
textvariables.create("TrainerControlPanel_AddTrainerFirstName", StringVar())
textvariables.create("TrainerControlPanel_AddTrainerLastName", StringVar())
textvariables.create("TrainerControlPanel_AddTrainerDOB", StringVar())
textvariables.create("TrainerControlPanel_AddTrainerAddress", StringVar())
textvariables.create("TrainerControlPanel_AddTrainerTelephone", StringVar())
textvariables.create("TrainerControlPanel_AddTrainerPostcode", StringVar())
textvariables.create("TrainerControlPanel_AddTrainerEmail", StringVar())

start_x = 0.3
start_y = 0.2
y_increment = 0.06
button_x_offset = 0.02
font_cfg = ("Arial", 15)

usernameLabel = lbl(fRoot.get("TrainerControlPanel"), text = "Username", font = font_cfg)
usernameLabel.place(relx = start_x, rely = start_y, anchor = "e")
usernameEntry = entryBox(fRoot.get("TrainerControlPanel"), font = font_cfg, textvariable = textvariables.get("TrainerControlPanel_AddTrainerUsername"))
usernameEntry.place(relx = start_x + button_x_offset, rely = start_y, anchor = "w")

passwordLabel = lbl(fRoot.get("TrainerControlPanel"), text = "Password", font = font_cfg)
passwordLabel.place(relx = start_x, rely = start_y + y_increment * 1, anchor = "e")
passwordEntry = entryBox(fRoot.get("TrainerControlPanel"), font = font_cfg, show = "*", textvariable = textvariables.get("TrainerControlPanel_AddTrainerPassword"))
passwordEntry.place(relx = start_x + button_x_offset, rely = start_y + y_increment * 1, anchor = "w")

firstNameLabel = lbl(fRoot.get("TrainerControlPanel"), text = "First Name", font = font_cfg)
firstNameLabel.place(relx = start_x, rely = start_y + y_increment * 2, anchor = "e")
firstNameEntry = entryBox(fRoot.get("TrainerControlPanel"), font = font_cfg, textvariable = textvariables.get("TrainerControlPanel_AddTrainerFirstName"))
firstNameEntry.place(relx = start_x + button_x_offset, rely = start_y + y_increment * 2, anchor = "w")

lastNameLabel = lbl(fRoot.get("TrainerControlPanel"), text = "Last Name", font = font_cfg)
lastNameLabel.place(relx = start_x, rely = start_y + y_increment * 3, anchor = "e")
lastNameEntry = entryBox(fRoot.get("TrainerControlPanel"), font = font_cfg, textvariable = textvariables.get("TrainerControlPanel_AddTrainerLastName"))
lastNameEntry.place(relx = start_x + button_x_offset, rely = start_y + y_increment * 3, anchor = "w")

dobLabel = lbl(fRoot.get("TrainerControlPanel"), text = "Birth Date", font = font_cfg)
dobLabel.place(relx = start_x, rely = start_y + y_increment * 4, anchor = "e")
dobEntry = DateEntry(fRoot.get("TrainerControlPanel"), font = font_cfg, textvariable = textvariables.get("TrainerControlPanel_AddTrainerDOB"))
dobEntry.place(relx = start_x + button_x_offset, rely = start_y + y_increment * 4, anchor = "w")

addressLabel = lbl(fRoot.get("TrainerControlPanel"), text = "Address", font = font_cfg)
addressLabel.place(relx = start_x, rely = start_y + y_increment * 5, anchor = "e")
addressEntry = entryBox(fRoot.get("TrainerControlPanel"), font = font_cfg, textvariable = textvariables.get("TrainerControlPanel_AddTrainerAddress"))
addressEntry.place(relx = start_x + button_x_offset, rely = start_y + y_increment * 5, anchor = "w")

telephoneLabel = lbl(fRoot.get("TrainerControlPanel"), text = "Telephone", font = font_cfg)
telephoneLabel.place(relx = start_x, rely = start_y + y_increment * 6, anchor = "e")
telephoneEntry = entryBox(fRoot.get("TrainerControlPanel"), font = font_cfg, textvariable = textvariables.get("TrainerControlPanel_AddTrainerTelephone"))
telephoneEntry.place(relx = start_x + button_x_offset, rely = start_y + y_increment * 6, anchor = "w")

postcodeLabel = lbl(fRoot.get("TrainerControlPanel"), text = "Postcode", font = font_cfg)
postcodeLabel.place(relx = start_x, rely = start_y + y_increment * 7, anchor = "e")
postcodeEntry = entryBox(fRoot.get("TrainerControlPanel"), font = font_cfg, textvariable = textvariables.get("TrainerControlPanel_AddTrainerPostcode"))
postcodeEntry.place(relx = start_x + button_x_offset, rely = start_y + y_increment * 7, anchor = "w")

emailLabel = lbl(fRoot.get("TrainerControlPanel"), text = "E-Mail", font = font_cfg)
emailLabel.place(relx = start_x, rely = start_y + y_increment * 8, anchor = "e")
emailEntry = entryBox(fRoot.get("TrainerControlPanel"), font = font_cfg, textvariable = textvariables.get("TrainerControlPanel_AddTrainerEmail"))
emailEntry.place(relx = start_x + button_x_offset, rely = start_y + y_increment * 8, anchor = "w")

TkImagePool.open("upload_pfp_img.png", "UploadPFP_Icon", (120, 120) )
pfpLabel = lbl(fRoot.get("TrainerControlPanel"), text = ("Upload Profile Picture (Optional)"), font = ("Arial", 14))
pfpLabel.place(relx = 0.83, rely = 0.22, anchor = "center")
pfpButton = Button(fRoot.get("TrainerControlPanel"), command = onUploadPfp, image = TkImagePool.get("UploadPFP_Icon"), activebackground = BG_ACCENT_COLOR, bg = BG_ACCENT_COLOR, borderwidth = 0)
pfpButton.place(relx = 0.83, rely = 0.235, anchor = "n")

#treeview widget
trainerControlPanelTVPopup = Menu(fRoot.get("TrainerControlPanel"), tearoff = 0)
trainerControlPanelTVPopup.add_command(label = "Update", command = partial(updateTrainer, True))
trainerControlPanelTVPopup.add_separator()
trainerControlPanelTVPopup.add_command(label = "Delete", command = partial(deleteTrainer, True))

trainerControlPanelTV = TV(fRoot.get("TrainerControlPanel"), "ID", "Username", "Password", "First Name", "Last Name", "Postcode", "Address", "Telephone", "DOB", "E-Mail")
trainerControlPanelTV.treeview.place(relx = 0.57, rely = 0.98, anchor = "s")
trainerControlPanelTV.treeview.bind("<Button-3>", partial(onTreeviewPopup, trainerControlPanelTV, trainerControlPanelTVPopup))

#buttons for trainer control panel
start_x = 0.98
start_y = 0.45
y_increment = 0.105
btn_width = 14

addTrainerButton = btn(fRoot.get("TrainerControlPanel"), text = "Add Trainer", width = btn_width, command = addTrainer)
addTrainerButton.place(relx = start_x, rely = start_y, anchor = "e")

updateTrainerButton = btn(fRoot.get("TrainerControlPanel"), text = "Update Trainer", width = btn_width, command = updateTrainer)
updateTrainerButton.place(relx = start_x, rely = start_y + y_increment * 1, anchor = "e")

deleteTrainerButton = btn(fRoot.get("TrainerControlPanel"), text = "Delete Trainer", width = btn_width, command = deleteTrainer)
deleteTrainerButton.place(relx = start_x, rely = start_y + y_increment * 2, anchor = "e")

#LESSON FRAME
textvariables.create("LessonControlPanel_TrainerId", StringVar())
textvariables.create("LessonControlPanel_LessonType", StringVar())
textvariables.create("LessonControlPanel_Duration", StringVar())
textvariables.create("LessonControlPanel_Date", StringVar())
textvariables.create("LessonControlPanel_LocationId", StringVar())
textvariables.create("LessonControlPanel_MaxPeople", StringVar())


fRoot.new("LessonControlPanel")
sidebar.addButton(os.path.join("menu_icons", "new_lesson_icon.png"), "LessonControlPanel")
sidebar.linkButton("LessonControlPanel", "LessonControlPanel")
addLogoHeader(fRoot.get("LessonControlPanel"), 0.076)

base_x = 0.31
x_offset = 0.03
base_y = 0.2
y_increment = 0.05
font_cfg = ("Arial", 12)

lessonTypeOptions = (
    "Spin Class",
    "Zumba",
    "Tabata",
    "Crossfit",
    "Yoga"
)

lbl(fRoot.get("LessonControlPanel"), text = "Trainer ID", font = font_cfg).place(relx = base_x, rely = base_y + y_increment * 0, anchor = "e")
entryBox(fRoot.get("LessonControlPanel"), font = font_cfg, textvariable = textvariables.get("LessonControlPanel_TrainerId")).place(relx = base_x + x_offset, rely = base_y + y_increment * 0, anchor = "w")

lbl(fRoot.get("LessonControlPanel"), text = "Lesson Type", font = font_cfg).place(relx = base_x, rely = base_y + y_increment * 1, anchor = "e")
menu = OptionMenu(fRoot.get("LessonControlPanel"), textvariables.get("LessonControlPanel_LessonType"), *lessonTypeOptions)
menu.config(font = font_cfg)
textvariables.get("LessonControlPanel_LessonType").set(lessonTypeOptions[0])
menu.place(relx = base_x + x_offset, rely = base_y + y_increment * 1, anchor = "w")

lbl(fRoot.get("LessonControlPanel"), text = "Duration", font = font_cfg).place(relx = base_x, rely = base_y + y_increment * 2, anchor = "e")
entryBox(fRoot.get("LessonControlPanel"), font = font_cfg, textvariable = textvariables.get("LessonControlPanel_Duration")).place(relx = base_x + x_offset, rely = base_y + y_increment * 2, anchor = "w")

lbl(fRoot.get("LessonControlPanel"), text = "Date", font = font_cfg).place(relx = base_x, rely = base_y + y_increment * 3, anchor = "e")
DateEntry(fRoot.get("LessonControlPanel"), font = font_cfg, textvariable = textvariables.get("LessonControlPanel_Date")).place(relx = base_x + x_offset, rely = base_y + y_increment * 3, anchor = "w")

lbl(fRoot.get("LessonControlPanel"), text = "Location ID", font = font_cfg).place(relx = base_x, rely = base_y + y_increment * 4, anchor = "e")
entryBox(fRoot.get("LessonControlPanel"), font = font_cfg, textvariable = textvariables.get("LessonControlPanel_LocationId")).place(relx = base_x + x_offset, rely = base_y + y_increment * 4, anchor = "w")

lbl(fRoot.get("LessonControlPanel"), text = "Max People", font = font_cfg).place(relx = base_x, rely = base_y + y_increment * 5, anchor = "e")
entryBox(fRoot.get("LessonControlPanel"), font = font_cfg, textvariable = textvariables.get("LessonControlPanel_MaxPeople")).place(relx = base_x + x_offset, rely = base_y + y_increment * 5, anchor = "w")

#treeview widget
lessonControlPanelTVPopup = Menu(fRoot.get("LessonControlPanel"), tearoff = 0)
lessonControlPanelTVPopup.add_command(label = "Update", command = partial(updateLesson, True))
lessonControlPanelTVPopup.add_separator()
lessonControlPanelTVPopup.add_command(label = "Delete", command = partial(deleteLesson, True))

lbl(fRoot.get("LessonControlPanel"), text = "Today's Lessons", font = ("Arial", 14)).place(relx = 0.58, rely = 0.73, anchor = "s")

lessonControlPanelTV = TV(fRoot.get("LessonControlPanel"), "ID", "Trainer ID", "Lesson Type", "Duration", "Date", "Location ID", "Max People", "Current People")
lessonControlPanelTV.treeview.place(relx = 0.57, rely = 0.98, anchor = "s")
lessonControlPanelTV.treeview.bind("<Button-3>", partial(onTreeviewPopup, lessonControlPanelTV, lessonControlPanelTVPopup))

#buttons for lesson control panel
start_x = 0.36
btn_anchor = "center"
start_y = 0.51
y_increment = 0.07
btn_width = 14

addLessonButton = btn(fRoot.get("LessonControlPanel"), text = "Add Lesson", width = btn_width, command = addLesson, padding = 0)
addLessonButton.place(relx = start_x, rely = start_y, anchor = btn_anchor)

updateLessonButton = btn(fRoot.get("LessonControlPanel"), text = "Update Lesson", width = btn_width, command = updateLesson, padding = 0)
updateLessonButton.place(relx = start_x, rely = start_y + y_increment * 1, anchor = btn_anchor)

deleteLessonButton = btn(fRoot.get("LessonControlPanel"), text = "Delete Lesson", width = btn_width, command = deleteLesson, padding = 0)
deleteLessonButton.place(relx = start_x, rely = start_y + y_increment * 2, anchor = btn_anchor)

today = datetime.today()
sview_cal = Calendar(fRoot.get("LessonControlPanel"),
                    showothermonthdays =False,showweeknumbers =False,
                    mindate=today,
                    date_pattern='dd/mm/yyyy',
                    justify="center",width=27,style="my.TButton",)
sview_cal.place(relx = 0.98, rely = 0.25, anchor = "ne")
sview_cal.tag_config("reminder", background = "red", foreground = "white")

def updateLessonCalendar():
    sview_cal.calevent_remove("all")
    records = db.retrieve("lesson")
    for row in records:
        s = f"""
        Date: {row[4]}
        Duration: {row[3]} {row[3] == 1 and 'hour' or 'hours'}
        Class Type: {row[2]}
        """
        sview_cal.calevent_create(datetime.strptime(row[4], "%d/%m/%Y"), s, "reminder")

def onCalSelected(arg=None):
    selectedDate = sview_cal.get_date()
    for row in db.retrieve("lesson"):
        if selectedDate in row:
            messagebox.showinfo("Class Alert", f"{row[2]} class on {selectedDate} for {row[3]} {row[3] == 1 and 'hour' or 'hours'}")

sview_cal.bind("<<CalendarSelected>>", onCalSelected)
fRoot.bindraise("LessonControlPanel", updateLessonCalendar )

#LOCATION FRAME
textvariables.create("LocationControlPanel_TrainerId", StringVar())
textvariables.create("LocationControlPanel_LocationType", StringVar())
textvariables.create("LocationControlPanel_Duration", StringVar())
textvariables.create("LocationControlPanel_Date", StringVar())
textvariables.create("LocationControlPanel_LocationId", StringVar())
textvariables.create("LocationControlPanel_MaxPeople", StringVar())


fRoot.new("LocationControlPanel")
sidebar.addButton(os.path.join("menu_icons", "new_location_icon.png"), "LocationControlPanel")
sidebar.linkButton("LocationControlPanel", "LocationControlPanel")
addLogoHeader(fRoot.get("LocationControlPanel"), 0.076)

base_x = 0.31
x_offset = 0.03
base_y = 0.2
y_increment = 0.05
font_cfg = ("Arial", 12)

locationTypeOptions = (
    "Spin Class",
    "Zumba",
    "Tabata",
    "Crossfit",
    "Yoga"
)

lbl(fRoot.get("LocationControlPanel"), text = "Trainer ID", font = font_cfg).place(relx = base_x, rely = base_y + y_increment * 0, anchor = "e")
entryBox(fRoot.get("LocationControlPanel"), font = font_cfg, textvariable = textvariables.get("LocationControlPanel_TrainerId")).place(relx = base_x + x_offset, rely = base_y + y_increment * 0, anchor = "w")

lbl(fRoot.get("LocationControlPanel"), text = "Location Type", font = font_cfg).place(relx = base_x, rely = base_y + y_increment * 1, anchor = "e")
menu = OptionMenu(fRoot.get("LocationControlPanel"), textvariables.get("LocationControlPanel_LocationType"), *locationTypeOptions)
menu.config(font = font_cfg)
textvariables.get("LocationControlPanel_LocationType").set(locationTypeOptions[0])
menu.place(relx = base_x + x_offset, rely = base_y + y_increment * 1, anchor = "w")

lbl(fRoot.get("LocationControlPanel"), text = "Duration", font = font_cfg).place(relx = base_x, rely = base_y + y_increment * 2, anchor = "e")
entryBox(fRoot.get("LocationControlPanel"), font = font_cfg, textvariable = textvariables.get("LocationControlPanel_Duration")).place(relx = base_x + x_offset, rely = base_y + y_increment * 2, anchor = "w")

lbl(fRoot.get("LocationControlPanel"), text = "Date", font = font_cfg).place(relx = base_x, rely = base_y + y_increment * 3, anchor = "e")
DateEntry(fRoot.get("LocationControlPanel"), font = font_cfg, textvariable = textvariables.get("LocationControlPanel_Date")).place(relx = base_x + x_offset, rely = base_y + y_increment * 3, anchor = "w")

lbl(fRoot.get("LocationControlPanel"), text = "Location ID", font = font_cfg).place(relx = base_x, rely = base_y + y_increment * 4, anchor = "e")
entryBox(fRoot.get("LocationControlPanel"), font = font_cfg, textvariable = textvariables.get("LocationControlPanel_LocationId")).place(relx = base_x + x_offset, rely = base_y + y_increment * 4, anchor = "w")

lbl(fRoot.get("LocationControlPanel"), text = "Max People", font = font_cfg).place(relx = base_x, rely = base_y + y_increment * 5, anchor = "e")
entryBox(fRoot.get("LocationControlPanel"), font = font_cfg, textvariable = textvariables.get("LocationControlPanel_MaxPeople")).place(relx = base_x + x_offset, rely = base_y + y_increment * 5, anchor = "w")

#treeview widget
locationControlPanelTVPopup = Menu(fRoot.get("LocationControlPanel"), tearoff = 0)
locationControlPanelTVPopup.add_command(label = "Update", command = partial(updateLocation, True))
locationControlPanelTVPopup.add_separator()
locationControlPanelTVPopup.add_command(label = "Delete", command = partial(deleteLocation, True))

lbl(fRoot.get("LocationControlPanel"), text = "Today's Locations", font = ("Arial", 14)).place(relx = 0.58, rely = 0.73, anchor = "s")

locationControlPanelTV = TV(fRoot.get("LocationControlPanel"), "ID", "Trainer ID", "Location Type", "Duration", "Date", "Location ID", "Max People", "Current People")
locationControlPanelTV.treeview.place(relx = 0.57, rely = 0.98, anchor = "s")
locationControlPanelTV.treeview.bind("<Button-3>", partial(onTreeviewPopup, locationControlPanelTV, locationControlPanelTVPopup))

#buttons for location control panel
start_x = 0.36
btn_anchor = "center"
start_y = 0.51
y_increment = 0.07
btn_width = 14

addLocationButton = btn(fRoot.get("LocationControlPanel"), text = "Add Location", width = btn_width, command = addLocation, padding = 0)
addLocationButton.place(relx = start_x, rely = start_y, anchor = btn_anchor)

updateLocationButton = btn(fRoot.get("LocationControlPanel"), text = "Update Location", width = btn_width, command = updateLocation, padding = 0)
updateLocationButton.place(relx = start_x, rely = start_y + y_increment * 1, anchor = btn_anchor)

deleteLocationButton = btn(fRoot.get("LocationControlPanel"), text = "Delete Location", width = btn_width, command = deleteLocation, padding = 0)
deleteLocationButton.place(relx = start_x, rely = start_y + y_increment * 2, anchor = btn_anchor)



#main procedure
if __name__ == "__main__":
    fRoot.show("Login")
    root.mainloop()
    

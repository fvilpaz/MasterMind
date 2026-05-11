# Transcripción — Lecture 1: C

---

## Welcome

All right, this is CS 50, and this is week one, our second week together, and you'll recall that last week, week zero, we focused on scratch ultimately this graphical programming language by which you can drag and drop puzzle pieces that interlock together only if it makes logical sense to do so. And many of you had actually probably played with that in like middle school or even prior at some point, but for our purposes, the goals of Scratch were to give us sort of a mental model for some fundamental constructs that we're going to see again and again today in C in a few weeks in Python, and even thereafter, and those include things like functions and return variables and arguments and variables and loops and conditionals and more.

And so even if today feels like a bit of a fire hose such as that pictured here, appreciate that a lot of today's ideas are exactly the same as last week's ideas. It's just that the syntax is going to change. It's going to look a little different. It's going to look a little scarier. It's going to be harder to sort of memorize except with practice will come that muscle memory, but the ideas ultimately are going to be the same.

And indeed this is, if unfamiliar, MIT down the road has a tradition of hacks whereby students once a year do something fairly crazy and at this point they happen to connect an actual working drinking fountain to an actual fire hydrant, and the sign there, very pixelated, says "Getting an education from MIT is like trying to drink from a fire hose." And that's indeed how computer science, how programming, how CS 50 will sometimes feel, but realize that what's going to be ultimately most important is not where you feel you are day after day, but where 3 months from now you feel that you are relative to last week alone, so-called week zero.

---

## Source Code

So let's look back at what week zero looked like. It looked a little something like this — the simplest of programs by which we get that cat to say Hello world. Today that same code is going to start to look a little like this, which was a glimpse we gave you last week. But this time I've deliberately color coded it to try to send the message that we're in Scratch — we had this yellowish puzzle piece that sort of kicked things off. That didn't really do anything itself, but it got the program started, whereas the real work was done in purple here. Same is going to be true today, whereby I'm going to wave my hands for a little bit of time at this yellowish code on the screen, but what's really going to have the most effect is this same purple line here and the white text within.

And we'll break down what all of these lines mean over the next couple of weeks, but sometimes we'll wave our hand at details if we feel it's a little unnecessary at this point in the story.

And in fact, let me get rid of the color coding for now and we'll see that this is the kind of code in a language called C we're going to start playing with and using today and for the next several weeks. And indeed it's representative of what we're going to generally call **source code**. So source code is what programmers write. It's what you write. It's what you wrote, albeit by dragging and dropping puzzle pieces. This week onward you're going to start using your keyboard all the more and you're going to write source code. So this is code that we humans can understand with some training and with some practice.

But of course per last week what language do computers ultimately understand? Only so binary — zeros and ones — and so you and I, yes, can write code starting today in a form that looks a little something like this, which admittedly might look a little arcane and cryptic, but it's certainly better than a whole bunch of zeros and ones. But we're going to write in source code, but the machines that we write code for ultimately only understand these here zeros and ones, which may very well say hello world, but we're going to call this moving forward **machine code**. So machine code is what the machines understand — only the zeros and ones. Source code is what you and I understand and actually write.

So it stands to reason that we're going to have to somehow translate one to the other — from source code to machine code. And I alluded to this ever so briefly last week, but we're going to use the same mental model whereby the source code we write might be the input to some problem. The output we want therefrom is going to be the machine code. So what we're going to equip you with today inside of this proverbial black box is a special piece of software that takes source code as input, produces machine code as output, and that type of program is called a **compiler**. And there's bunches of different compilers in the world. We're going to have you use one of the most popular ones, but it's simply a piece of software that someone else wrote that converts one language to another — source code, for instance, in a language called C, to machine code, the zeros and ones that our Macs, PCs, phones, and other devices actually understand.

---

## VS Code / cs50.dev

So where are we going to do this and how are we going to do this? So I promised last week that we'd introduce you to this tool, which I used briefly at the very start of class to whip up that chatbot. We're going to use it though not for Python this week, but indeed for a different language C. And indeed this tool, Visual Studio Code or VS Code for short, is super popular in industry. This is what real programmers, so to speak, are using all of the time nowadays. There's absolutely alternatives. If some of you have programmed before, you might have used or experienced different tools, but this is a very common tool that you'll see even after CS 50, and in fact it's something that ultimately you can install for free on your own Macs and PCs so that by the end of the course you're completely independent of CS 50 and any CS50 related tools.

But what we have done for the very start of the class is essentially provided you with a cloud-based version of this tool. So all you need is a web browser on any Mac or PC or the like, so that everything's pre-installed for you, pre-configured for you, and you don't have to deal with the stupid technical support headaches at the start of the term because it should just work. But by the end of the term, once you're a little more comfortable with technology and with code in particular, you can absolutely offboard yourself from this tool, install it, download it on your own Mac and PC, and have pretty much the exact same environment completely under your control.

So starting today, you're going to see an interface that looks quite like this quite often, and we use this same interface last week ever so briefly. Moving forward, here's where we're going to write code — at top right is where one or more code tabs are going to appear similar to any tabbed environment that you might use. Here, for instance, is just a screenshot of the first file we'll create today called `hello.c`. The reason it's called `hello.c` is because it's in a language called C, as we soon shall see.

Meanwhile, the code here happens to be color coded, not quite in the same way as you saw before, because I manually made it look more like Scratch blocks. But among the features that VS Code and other programming environments provide — something called **syntax highlighting** — whereby you don't worry about or even think about these colors, but as you write out code in a recognized language, tools like VS Code will just color code different parts of your code for you just to make different features jump out.

You'll also spend a good amount of time, as I briefly did last week, down here in the bottom right of your screen, the so-called terminal window, which is going to be where you run commands for compiling code and writing code. And in fact, as we'll see today, you're going to start using your mouse and clicking a little bit less. You're going to start using your keyboard and typing a bit more. And ultimately, even though at first that might feel like a step backwards to sort of not use something that's so user friendly, the reality is most every programmer tends to find themselves ultimately much more productive, much more powerful, using the keyboard more often, more quickly than, say, a traditional mouse or trackpad would allow.

Meanwhile, we'll see some somewhat familiar features. Here at left is where you'll see the files and folders that we will create over time. At far left here is going to be an activity bar, which is essentially a modern form of a menu via which you can open and close things and access other features. For my purposes, I'll generally hide this part here so that when we're together we're focusing almost entirely on code and commands.

So with all that said, just some terminology. This whole collective environment that I'm describing here is generally what's known as a **graphical user interface**. Why? Well, it's an interface for users that's graphical in nature with icons and buttons and the like. Shorthand notation for this is GUI. But within this graphical user interface, as promised, is going to be that terminal window at bottom right where I promised we would be typing most of our commands. And just to give you a bit more jargon in computing, that's generally known as a **command line interface**, or CLI, whereby you're typing commands into that interface instead. The world of computing software is essentially divided into GUIs and CLIs, and sometimes a piece of software might have one of each as well.

---

## Hello World

But without further ado, why don't we go ahead and focus entirely first on this here program, which I dare say is the simplest program you can write in a language like C and see how we can actually compile and run it together. So I'm going to go over to VS Code here. I've hidden my File Explorer with all the icons and I've hidden my activity bar so that only do I have room for tabs of code and the command prompt at the bottom.

I'm calling this a command prompt because it's at this dollar sign where I'm going to run some of my commands, and it's a dollar sign by convention. It has nothing to do with currency. It's just a computing convention. Some systems will use a carrot symbol, some systems will use a greater than symbol rather, or something else, but it just means type your commands here.

The first such command I'm going to type is this:

```bash
code hello.c
```

With a single space in between. I've not used any spaces in the name of the file. I've not capitalized any aspect of the file just because this is convention, unlike your Mac or PC, where you might be in the habit of naming files with spaces and capitalization. Generally you'll make your life simpler by just using lowercase and no spaces at all. As soon as I hit enter, what you'll see is that a brand new tab appears called `hello.c` with a cursor blinking on line 1. And this is essentially VS Code waiting for me now to type the first line of my code.

So let's go ahead and whip up this code. In this tab I'm going to do `#include <stdio.h>`, in `main(void)`, then inside of so-called curly braces indenting therein by 4 spaces, I'm going to say `printf("hello, world\n");`, and voila, I've written my first program in C.

```c
#include <stdio.h>

int main(void)
{
    printf("hello, world\n");
}
```

In a class like this, no need to write down each and every line of code that I write. In fact, on the course's website will be copies of everything that we've done as well as excerpts therefrom in the course's notes.

So that's it. Like I've written my very first program. And in this specific programming environment that has a mix of a GUI and a CLI, I actually need to click down in my terminal window, and I need to now compile this program first because at this point in time it exists only as source code. So to do this, I'm going to compile my code by very aptly saying:

```bash
make hello
```

Make space hello — as it sort of implies, some magic will make a program called hello. Notice I have not said `hello.c` again because the compiler, let's call it Make for now, even though that's a bit of a white lie, is going to infer that if I want to make a program called hello, it's going to automatically look for a file called `hello.c` in this case.

And remarkably, any time you don't see any output at a command like this, that's probably a good thing. Generally speaking, when you see output when compiling your code, you have done something wrong. So no output is good, because what I can now do is run this program not by double clicking or tapping anywhere, but by doing:

```bash
./hello
```

And this is a bit weird, but what the slash means is that after having just made a program called hello, that program's going to end up in my current folder. When I say `./`, that's like saying go into the current folder and run the program therein called hello specifically. Now, as I often do, I'll cross my fingers, hope that I didn't mess this up in any way, and I should see in a second — "hello, world" indeed printed onto the screen.

And so just to recap those commands: one, I ran `code hello.c`, which is a VS Code specific thing — `code` short for VS Code, just creates a new file called `hello.c` and then I'm on my way with my own keyboard. `make hello` compiles that source code into machine code, thereby creating a new file called hello, and to run that program hello, I type this strange command `./hello`. But this is a paradigm no matter what you call your programs, we're going to see again and again and again.

---

## From Scratch to C

So let's tease apart what it is we just did and like why this code works in the way that it does. Well, to recap, in Scratch, we had a program like this. When the green flag was clicked, we wanted to say "hello world" onto the screen. The code that corresponds to that is roughly here and indeed notice that the yellowish or orangeish code lines up with the "when green flag clicked," the purple code here lines up with the same block, and the white code inside of here roughly corresponds to what was in the white oval that we kept using again and again last week.

So let's do more of a one-to-one correspondence — and these slides are deliberately designed to give you again that sort of mental model of taking same ideas from last week and just changing the syntax this week onwards. So when we have a function like this thing here, and recall that a function is just an action or verb, it sort of accomplishes a small piece of work — in code in C specifically, you're going to type, of course not a purple puzzle piece, but you're going to say the word `printf` — more technically `printf`, where the `f` as we'll soon see, means format the printed output, because this is more powerful than just printing some raw text alone. Then you can have parentheses open and closed left and right, and notice that it's no accident that MIT chose an oval for their input to functions because it roughly looks like the start of a parenthesis and parenthesis on left and right.

Meanwhile, what goes inside of the parentheses in the corresponding C code? Well, at the end of the day, minimally "hello, world" because that's literally what we want to print to the screen. But in C, unlike in Scratch, there's a bit of overhead, a bit of additional syntax that you just got to deal with to make clear to the computer what you want to print. In particular, you're going to have to surround everything you want to print with double quotes to make clear that hello is not some special function or variable or something else. "Hello world" is the English phrase that you want to print. So double quote here, double quote there means here's the beginning and the end of what I want to print.

You're also curiously going to put a `\n` in most cases at the end of the word or words you want to print. We'll take that away in a moment and see what it does. And then lastly and perhaps most annoyingly in programming circles, you have to finish your thought with a semicolon, much like in English you would finish most sentences with a period instead.

And the thing about programming is with C in particular, if you mess up almost any of these details I just rattled off, something's going to go wrong. And so you're in good company. The very first program you try to write or try to compile, odds are it might not work correctly because you'll develop over time the muscle memory for spotting all of these seemingly minor — and actually minor — details but that do matter to the computer.

All right, so if you're familiar, of course, with the notation in like mathematics of functions — like a function in code, it's really the same idea as a function in math whereby the function F takes some input, for instance X, and generally produces some output. So if you're coming more from that background, realize that what we're really doing here is roughly the same.

But in code, recall that we can have different types of output. So if this is our grand mental model and say we've got a function inside of this black box that takes arguments — that is to say its inputs — it can sometimes have **side effects** and recall that side effects are often visual things that happen as a result. They just play on the screen, maybe it comes out of the speaker. It's something generally ephemeral that just happens, but it's not necessarily useful in the same way as another type of function that we'll return to in just a bit.

But last week recall that we got the cat with the speech bubble to manifest on the screen and say "hello world" in that speech bubble when the input was "hello world" and the corresponding function was instead "say."

So let's see if we can't now tease apart what the code we wrote is actually doing for us bit by bit. So let me go back to VS Code here and let me propose to break this in a little way. Let me delete the `\n`, if only because at first glance, who knows or cares what that's doing. Let's just get rid of it if we don't understand it. I could now go back down to my terminal window and I could do `./hello` enter again, but there's seemingly no change. Which is good, doesn't seem like I broke it, but I've kind of misled you here — why? Why did nothing seem to change? I didn't recompile it. So recall that the compiler converts source code to machine code, but I already did that a couple of minutes ago. If I've changed the source code, it stands to reason that I need to recompile the code to actually see the effects of that. So let me do that again. `make hello`. Nothing seems to have gone wrong, but let me now do `./hello`. And it's subtle — the backslash N apparently adds a new line. It's just an aesthetic bug insofar as functionally the program is still technically printing "Hello world", but what's seemingly wrong is that if this dollar sign represents my prompt where I type commands, it just looks kind of stupid that I finished a program over here and then the prompt is on the same line.

So what would the alternative be? Well, what you're seeing here is what's actually generally known as an **escape sequence**, which are sort of special sequences of symbols like `\n` in this case that do a little something unusual. And here's just a non-exhaustive list of some you'll encounter in the real world and including in CS 50:

- `\n` — moves you to a new line
- `\r` — a so-called carriage return, moves the cursor horizontally as opposed to vertically
- `\"` — a backslash double quote: used when you want to print an actual double quote character inside a string, since you can't put a raw quote inside quotes

But let me go back to the code and propose what the alternative otherwise might have been. If I didn't know about `\n`, my instinct to move the cursor to the next line might have been literally to just hit enter or move the double quote, move the parenthesis, move the semicolon onto the next line. But this should start to rub you the wrong way. And indeed this violates a principle of most programming languages — most programming languages are line based. You sort of start and finish your thought ideally on the same line. So C and many other languages solve this by giving you these so-called escape sequences.

Now that's a bit of an overstatement — what I said — in that sometimes lines of code will be so long that they do wrap onto multiple lines, but generally that's a convention that we're going to try to avoid.

---

## Header Files and CS50 Manual Pages

All right, what else could go wrong? Well, let's do this. Let me go ahead and suppose I forgot to include the header file `#include <stdio.h>` at the top. You would think this is enough, just printing out "Hello world." Well, let me go back down to my terminal window. Let me do `make hello` again now, and I'm going to get a whole different error message instead. The problem is still with `hello.c`. Line 3, somewhere in there `printf` is suddenly the problem even though the semicolon is back and the `\n` is back. The error says: `error: call to undeclared library function printf`.

So here is an example of an error message that unless you're sort of conditioned to know what this means and you've seen it before, it's quite more cryptic and unclear. Especially when the rest of your code is truly correct — I've just forgotten something stupid. But how can I sort of think about this problem?

Well, it turns out that another feature of C is that it comes with a bunch of **header files** — files whose names don't end in `.doc` but end in `.h`. These so-called header files contain code that other people wrote that you can use in your own programs. For instance, in this particular case, a header file is giving us access to what's more generally in computing called a **library** — a library is code someone else wrote that you can use.

So for instance, even though `printf` is a feature of C, if you want to use it, you have to include that library by telling your program to include the header file that defines that function. And you only know this by being taught it or looking it up in a book or a reference, but in this case I wanted to use a header file called `stdio.h`. It is not `studio.h` — this is a very common bug online if you find yourself typing `studio.h`. It's `stdio.h`, and in that file then is defined the `printf` function. So if I go back to my code here, the solution to this problem truly is to just undo the deletion I made a moment ago because what line one is now doing for me is it's telling the compiler — oh by the way, I didn't write all of the code that I'm about to use. Please include the definition of `printf` from this other file called `stdio.h`.

So where do you look stuff up? Well, it turns out the ecosystem of C has hundreds of books you can buy or download, many many websites. Among them is one of CS 50's own. And in fact the conventional way to look stuff up for the programming language called C is to look at the official manual pages or man pages for the C language. Unfortunately, many of them were written decades ago — certainly written by fairly advanced programmers and not for a broad audience. And so what we have done is imported all of that freely available documentation, hosted it at our own URL here, `manual.cs50.io`, and we've essentially simplified it for those less comfortable, those of you who might be less familiar with technology, and really for most people who aren't used to reading manual pages — it's just useful to have it written in teaching assistant-like language instead.

For instance, if you go to a URL like `manual.cs50.io`, you'll see CS 50's documentation for this official library `stdio.h` that comes with C itself. If you go to a specific page like `stdio.h`, you'll see for instance just over a half dozen functions that we won't touch on today beyond `printf`, but that we'll see in the class over time that does useful stuff — for instance `printf` prints to the screen and we'll see other functions for opening files, closing files, and the like.

But what we're also going to see is that besides these official functions, there's some that CS 50 itself has invented. We use these really as training wheels for just the first few weeks of the course, and then we take these training wheels off. But the reality is in a language like C, certain stuff is just really hard or annoying to do. So for instance, at this URL here you can see documentation for CS 50's own library and CS 50's own header file `cs50.h`, and you'll see such functions in the documentation as these: `get_string`, `get_int`, `get_char`, and a bunch of others as well, and we'll touch on those this week.

So let's focus, for instance, on one of these first — `get_string`. A **string** in programming speak means text — zero or more characters of text like H E L L O W O R L D. That is a string of text in computer speak and it's obviously not a number like 50, it's actual text that you would type on the keyboard. With this function, we can start to replicate another program that we implemented pretty quickly last week in Scratch.

---

## Hello, You

So recall that in Scratch this one was a little more interactive. I used another blue puzzle piece "ask" to actually get input from the user. And recall that unlike the `printf` function today and the same block last week, this time we still have the same input/output model, but if we pass an argument to a function that we're about to see, you can get back not just a side effect sometimes but a **return value** — like a useful reusable value like the person's name, as we'll soon see.

All right, so let's actually do this. If in Scratch the equivalent was asking the user "what's your name?", asking them that, and then waiting for an answer that we can store in a variable, let me propose that in C side by side it's going to look a little something like this. Instead, the closest analog in C, thanks to CS 50's library, is going to be a function called `get_string`. So there's no C function called "ask" — and we deliberately named this function `get_string` just to make super clear what it is you are getting — a string of text in this case, and we've got the parentheses ready to go.

If I want to prompt the user with that same phrase, "what's your name?", well, I can just put it inside of those parentheses. But what next do I need to add around my user input? Yeah, I need the quotation marks just to make clear that these aren't special individual words. This is a whole phrase that I want to be displayed to the user.

Now we're not done yet. Because we need to do something with this value. The `get_string` function is going to prompt the user for me to type something in like my name, but where do I want to put that? Well, MIT has the answer — put it in a variable called "answer", and you can't rename that in Scratch. But in C, what I'm going to need to do is something like this. If you want to keep return values around from a function, you literally use an equal sign, and then to the left of it you put the name of the variable into which you want to put that return value. So in mathematics we would use X, Y, and Z as our variables. Again in code, as in Scratch, you can name your variables anything you want. By convention they should usually be lowercase, they should not have spaces therein, similar to file names.

But C is a little more precise. You can't just give the variable a name. You need to tell C — or really the compiler — what type of value you want to put in this variable. So if it's a string of text, you put `string`. If it's a number, you're going to put something else. But for now it's a string, per the function's name, it's going to give me a string. Now we're so close to finishing this — there's one detail missing. What's still missing from the code here? Yeah, we have to finish the thought lastly with a semicolon.

Now let me do something intuitive but not quite correct. If I want to print out that answer so that the expression is going to be not "hello world" but "hello David" or "hello Kelly", let me go ahead and say `printf("hello answer\n");`. So this is not quite right — and even if you've never programmed before, you can perhaps see where this is erroneously going. Let me remake the program. Nothing seems to be wrong syntactically, but if I do now `./hello` and hit enter, you'll see I'm being prompted "what's your name?" So I'm going to go ahead and type in David and then hit enter. And what am I going to see instead? "hello answer" — and the computer's just doing literally what I told it to do. I said quote unquote print out "hello answer", but obviously that's not the goal that I have in mind.

So how do I actually work around that? Well, what I really need to do is achieve the equivalent of the join block from Scratch. We can do this by using special syntax to indicate where I want the person's name actually to go. Let me propose that we now do this. Instead of printing out "hello answer", let's go ahead and start printing out something, and we've got parentheses ready. I want to somehow now say "hello, placeholder." And you would only know this by someone having told you or a reference online — `%s` is the placeholder for a string that you don't know when you're writing the code, but when someone else is running the code, it will be filled in and substituted for their input.

So the syntax becomes:

```c
printf("hello, %s\n", answer);
```

This is telling `printf`: print out "hello, " — then something. What should I probably pass in to these parentheses as a second input so that `printf` knows what that something is? Yeah — the variable name. So the variable in which I have the user's name. And indeed the convention is to put a comma after the quotes and then the name of the variable that has the value you want to be substituted for that placeholder.

Notice there's a collision of syntax and grammar here. The comma inside of the quotes is just an English thing — "hello, so-and-so." The comma outside of the quotes is meaningful to C because it delineates which is the first input or argument to the left and which now is the second. And we haven't seen this before in C — up until now we've only been passing one input, but you can pass in 2 or 3 or 4 — it completely depends on what the function is designed to expect.

So the full program now looks like:

```c
#include <cs50.h>
#include <stdio.h>

int main(void)
{
    string answer = get_string("What's your name? ");
    printf("hello, %s\n", answer);
}
```

Let me go back to VS Code. Previously we were literally printing out "answer", but I can change it to `%s`. I can move my cursor outside of those quotes, comma `answer`, because that's the name I gave to that variable. Let me go back down to my terminal window, clear it just to reduce clutter. Let me do `make hello` one more time. Seems to work. `./hello`, DAVID, and now "hello David" is printed.

---

## Linux

OK, so if we now have that done, well, let's just take a step back into the first question that was just asked about where are these files. Let's take a look back at actually what it is we're actually using here.

So it turns out, even though most of you are using Mac OS or Windows, there's other operating systems out there in the world. Phones have iOS, iPads have iPadOS, Android devices have Android, which is its own operating system. The operating systems in the world are the pieces of software that really just do the most fundamental operations on a device — like booting it up, shutting it down, sending something to a printer, displaying something on the screen, managing windows and icons and all of that sort of commodity stuff that is used by other people's software as well.

A very popular operating system in the programming world and in the world of servers in the cloud and on the internet at large is called **Linux**, and it's a descendant of something called Unix, which has been around for quite some time, and it's what many programmers, most programmers use depending on their environments, insofar as Linux is very highly performant — you can support thousands, millions of users on servers running an operating system like this. Linux, insofar as it's usually used as a command line interface, comes with a whole bunch of commands that you'll start to use and see over time.

Now I've used a bunch of commands already. I've used `code`, which is a VS Code thing. I have used `make`, which is for today's purposes our compiler, but that's a little white lie that we'll distill next week. And then I've used `./hello`, which is a command I essentially invented as soon as I created a program called hello. But there's a bunch of other ones as well:

- `ls` — list the files in my current folder
- `mkdir` — make a directory (create a new folder)
- `rm -r` — remove a directory
- `rm` — remove a file
- `mv` — rename or move a file
- `cp` — copy a file
- `cd` — change directory (change into a folder)

Now these just take a little bit of time and practice to memorize them, and they're all very terse insofar as the whole point of a command line interface is to let people navigate things quickly.

So for instance, even though this will be a bit of a whirlwind, let me go back into VS Code and let me propose that we play around with just a few of these commands. So let me go ahead and reopen my file explorer at left. Yours will look a little different. You'll have a different number as your unique ID, but generally you'll see whatever files and or folders you've created already. The first thing I created today was called `hello.c`, and then by using Make, I created a second file called `hello`. So the reason `./hello` works is because there is in fact a program called `hello` in my current folder, which was created when I compiled my source code into machine code.

Now suppose for the sake of discussion that this is going to get messy quickly because the more programs we create in class and for problem sets, you're just going to have a hot mess of files inside of this one main folder. Well, let's create subfolders like you might be inclined to do on your Mac or PC or Google Drive or whatnot. I could right click or control click on my File Explorer and I'll see a somewhat familiar contextual menu, and I can literally choose "new folder" — or I can rename things or I can move things around by dragging and dropping them. But for today, let's focus more on the CLI and commands like these.

So let me go back into VS Code. Let me delete the machine code. I'm done with this example. I don't really want to keep these bits around unnecessarily. I'm going to delete hello, not `hello.c`, but `hello`, the compiled program. When I type `rm hello`, I'll be cautioned — "remove the regular file called hello?" Here I'm being prompted for a yes/no response. Y suffices. So I'm going to hit Y enter and watch what happens at top left — as soon as I use this command to remove that file, it disappears.

Now let's create a new folder:

```bash
mkdir hello
```

Now I indeed have a folder and it even has an obvious folder icon next to it. Now I could click and drag on `hello.c` and just drop it into hello, but let's stick with the command line interface. Let me go ahead now and move with `mv`:

```bash
mv hello.c hello
```

The way the move command is designed is to expect the origin as the first word and the destination as the second. Because the hello folder already exists, Linux knows what it's doing and it's just going to put `hello.c` into that folder.

Now let me type `ls`. And when I type `ls` for list, you'll see only a folder called `hello`, and it's color coded just to call it out. Now I need to change into that folder:

```bash
cd hello
```

My prompt has now changed — it still has a dollar sign, but before it is just a constant reminder of what folder I am in. Now if I type `ls`, I should see just `hello.c` because that's the only thing in that folder. Let's do `make hello` inside of this folder:

```bash
make hello
./hello
```

Now I've got both files. I can also `rm hello` to remove the compiled program, rename a file with `mv hello.c old.c`, and copy with `cp hello.c backup.c`. The point here is just to demonstrate that with these basic fundamental commands you can do everything that you've taken for granted on Macs and PCs for years with a mouse instead.

And when in doubt or if you ever get yourself into a confusing mess, just type `cd` enter alone and you'll be magically whisked away to your default folder, a home directory, so to speak, which leads you always to where you start when logging in to `cs50.dev`.

Two special notations worth knowing:

- `.` (single dot) means this folder
- `..` (two dots) means the parent folder, one step up in the hierarchy

So to move a file out of a subfolder:

```bash
mv hello.c ..
```

---

## Conditionals

All right, so let's introduce a few more building blocks and a few more things we can do. So besides these Linux commands, which we'll now start taking for granted, we have a bunch of other features of programming languages that we saw in Scratch. Let's now translate them to C.

So **conditionals** were sort of the proverbial fork in the road, enabling you to do this or this or some other thing based on the answer to a question, a so-called Boolean expression. Here, for instance, in Scratch is how we might express if a variable X is less than a variable Y — we'll go ahead and say "x is less than y." In C, the way you would do the same thing is:

```c
if (x < y)
{
    printf("x is less than y\n");
}
```

You say `if` and then a space, then parentheses — which have nothing to do with functions; `if` is not a function, it is a feature of C that implements conditionals. Inside of the parentheses you put your Boolean expression. And the answer, even though it's a less than sign, is indeed going to be true or false — yes or no. It's a Boolean expression. It either is less than or it is not.

Inside of the curly braces which are necessary here, I'm just going to literally put `printf`. This is deliberate — just like in Scratch the "say" is indented and sort of hugged by the if orange puzzle piece. Similarly, these curly braces are sort of embracing these lines of code. As an aside, in C, they're not always necessary if you have a single line of code. However, you'll see that in CS 50 in particular we will generally preach a certain style — like any company in the real world would do — so that programmers who are collaborating on code all write code that looks the same. And then I've indented 4 spaces to make clear logically that this line of code only executes if the answer to this question is true.

Meanwhile, in Scratch, if we had an if/else condition — a two-way fork in the road — if X is less than Y, say so, else say X is not less than Y. How can I do that in C?

```c
if (x < y)
{
    printf("x is less than y\n");
}
else
{
    printf("x is not less than y\n");
}
```

How about something a little more involved? If X is less than Y, then say X is less than Y. Else if X is greater than Y, then say X is greater than Y. Else if X equals Y, then say X is equal to Y:

```c
if (x < y)
{
    printf("x is less than y\n");
}
else if (x > y)
{
    printf("x is greater than y\n");
}
else if (x == y)
{
    printf("x is equal to y\n");
}
```

Before we reveal what's in the curly braces, this is not a typo — why have I presumably done `==` (double equals) even if you've never used C before? Because the single equal sign, which we've used already when storing a value from `get_string` into a variable like `answer`, is technically the **assignment operator**. So humans decades ago decided that when faced with a situation where they wanted to copy from the right to the left a return value into a variable, it made sort of visual sense to use an equal sign. But they'd already used equals for assignment. So the solution in C as well as in many other languages is literally two equal signs — the **equality operator**, whereas a single one is the assignment operator.

But here's an opportunity to distinguish a missed design opportunity. The above code is arguably not well designed, even though it is correct — because we don't need to ask this third Boolean expression `x == y`. Well, logically, if we're using normal numbers, it's either less than or greater than or by default equal to. So you're just wasting the computer's time. A slightly better design uses `else` without a condition at the end:

```c
if (x < y)
{
    printf("x is less than y\n");
}
else if (x > y)
{
    printf("x is greater than y\n");
}
else
{
    printf("x is equal to y\n");
}
```

A minor optimization, but you can imagine doing that again and again and again in your code — you don't want to be wasting the computer or the user's time if you can improve things.

---

## Types

All right, so now that we have these equivalences between Scratch code and C code for these conditionals, well, what other things can we throw into the mix? Well, C has a whole bunch of operators, and just so that you've seen a list in one place:

- `=` — assignment
- `<`, `>` — less than, greater than
- `<=`, `>=` — less than or equal to, greater than or equal to
- `==` — equality operator
- `!=` — not equal (the exclamation point implies negation)

And there's many other operators that we'll encounter in the wild over time. But there's also worth noting in C more than just strings — there's other types of data that you might get from a user or store:

- `bool` — a variable that can be true or false, and that's it (very much interrelated with Boolean expressions)
- `char` — a single character, not strings of text like multiple letters and words, but just individual characters
- `float` — a floating point value (a number with a decimal point, a real number); a float generally uses nowadays 32 bits total to represent those numbers
- `double` — like a float but using 64 bits, which is way more precise (twice as many bits), but it doesn't fundamentally solve the problem because it's still finite and not infinite
- `int` — simple integers 0, 1, 2, and the negatives thereof; those conventionally use 32 bits, which means the highest a computer can count using an int would be about 4 billion (but if you want to do negative numbers, it's going to be roughly negative 2 billion to positive 2 billion)
- `long` — uses 64 bits, which is a much bigger range of values, but there too still finite

The catch with floats and the finite representation is that how many total values can you represent with 32 bits? It's roughly 4 billion per last week. But how many real numbers are there in the world according to math class? An infinite number. So we seem to have a mismatch between what we can represent in code and how many actual numbers there are in the world.

A couple of those types come from `cs50.h`. So among the things you get by including `cs50.h` in your code is access to not only `get_string`, but these other functions as well:

- `get_string`
- `get_int`
- `get_char`
- `get_double`
- `get_float`

We don't have a `get_bool` because it's not really useful to just get a true or false value typically, but we could have invented it. But we'll frequently use these here functions that you can access by using that header file.

---

## Format Codes

But where are we going to put these values and how are we going to display them? Well, it turns out there's more than just `%s`. So `%s` was a placeholder for a string, but if you want to print out something like:

- `char` — single character → `%c`
- `float` — floating point value → `%f`
- `int` — integer → `%i`
- `long` — long integer → `%li`

In short, there are solutions to all of these problems. These are not intellectually interesting details, but they are useful, practical things to eventually absorb over time.

---

## Variables

So let's actually use these techniques in some code. But before we get to that, let's focus on variables. In Scratch we had the ability to store a bunch of values in variables that we could create ourselves. In C you can essentially achieve the same. So for instance, suppose that in Scratch we wanted to keep track of someone's score using a counter — well, we might create a variable called `counter` and set it initially to 0 and then eventually add 1 to it. Well, in C:

```c
int counter = 0;
```

You choose the name of your variable, you assign it a value like 0 initially, but per earlier — what more am I probably going to have to do in C? Yeah, I've got to give it a type. And a counter insofar as it's numeric is not going to be a string of text. So `int` will suffice. One minor thing missing: the semicolon to finish the thought.

Suppose that in Scratch you wanted to increment the counter and add 1 to the score. It might look like "change counter by 1". In C you can do this actually in a few ways:

```c
counter = counter + 1;
```

This takes whatever the current value of counter is — 0 — adds 1 to it, and then stores that 1 in the counter variable. So now the value is 1. But honestly, this incrementation technique is so common that there's more shorthand notation:

```c
counter += 1;
```

Looks a little weird at first glance, but `counter += 1;` does the exact same thing. You can just type fewer keystrokes. And doing this is so common in C that you can even do:

```c
counter++;
```

`counter++` does the exact same thing by adding one to the variable. There's no `+++` or more pluses — it's only for incrementing individual values by one. And there are equivalents for decrementation (`counter--`) and doing minus or the minus symbol more generally.

---

## compare.c

All right, so let's actually use this technique in some code. Let me go back into VS Code. Let me close my file explorer and let's go ahead and create a program called `compare.c` to compare some values. Let me do `code compare.c` to create a brand new program, and then I'm going to include `cs50.h` and `stdio.h`, do `int main(void)`, and then inside the curly braces let's use these new techniques.

```c
#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int x = get_int("What's x? ");
    int y = get_int("What's y? ");

    if (x < y)
    {
        printf("x is less than y\n");
    }
    else if (x > y)
    {
        printf("x is greater than y\n");
    }
    else
    {
        printf("x is equal to y\n");
    }
}
```

It's not that interesting of a program, but it's at least dynamic in that now I'm prompting the user for two numbers. So let's do `make compare`. Seems to have worked. And in fact I can check that it worked by typing `ls`. Now you'll see I've got `hello.c` — no `hello` because I deleted that — I've got `compare.c` which I just created, and then I've also got a program called `compare` and the asterisk there is just a visual indicator that this is executable, it's a program you can run.

If I now do `./compare`, let's do something silly like 1 for X, 2 for Y. OK, "x is less than y." Let's do it again — 2 for X, 1 for Y. And I see nothing. Well, why am I seeing nothing? Well, logically, I didn't have a condition for checking for greater than. So I added the else if and else, and now let me clear my terminal window, do `make compare` again, `./compare` 1 and 2 works exactly the same. Now let me go ahead and do 2 and 1 — there we have better output. And if I do 1 and 1, well it's not wrong to say "x is not less than y", but it's not very precise. With the complete if/else if/else version, we catch all three situations.

Why not use three separate if statements instead of if/else if/else? Because then it would check each and every condition, even though for example the first one might be fulfilled, it would check the 2nd and 3rd too. Exactly — it's another example of bad design because now no matter what you're asking three questions. Even if X ends up being less than Y from the get-go, you're still wasting everyone's time by saying, "Well, is X greater than Y? Is X equal to Y?" So a cleaner design uses the if/else if/else structure.

---

## agree.c

Let me close `compare.c`. Let me reopen my terminal window and clear it, and let's create a program called `agree.c`. It's all too often nowadays that we have to agree to terms and conditions. Let me go ahead and include `cs50.h` and `stdio.h` and do `int main(void)`.

Now for a yes/no answer, it suffices just to ask for a single char or character, not a whole string. So:

```c
#include <cs50.h>
#include <stdio.h>

int main(void)
{
    char c = get_char("Do you agree? ");

    if (c == 'y' || c == 'Y')
    {
        printf("Agreed.\n");
    }
    else if (c == 'n' || c == 'N')
    {
        printf("Not agreed.\n");
    }
}
```

Notice on lines checking `'y'` and `'Y'` I've used single quotes, which I alluded to earlier. Why is that the case? Yeah — it's a single character, and this is just the way you do it in C. When you want to compare a single character, you use chars and you use single quotes. When you want to use strings of text — like multiple characters, multiple words, multiple sentences or paragraphs — you use strings. So this would seem to work.

Now let me go ahead and do `make agree` and then `./agree`. Do I agree? Sure, I'm gonna go ahead and type Y. But suppose I type uppercase Y — well that only works because of the `else if`. And if I type Y in uppercase and it didn't work, that seems like a bug. So how can we fix this? Well, notice using `||` (logical or) — two vertical bars — I am now taking a Boolean expression and composing it from two smaller Boolean expressions, and I care about the answer to one of those questions being true. Whether it's lowercase y or uppercase Y, this code now will work.

The two vertical bars mean **logical or**. And you could also use two ampersands `&&` to connote **and** in other contexts. But for this case, `||` is correct — the variable can't be both lowercase and uppercase at the same time, so "and" would make no sense here.

---

## Loops and meow.c

All right, well let's do one final flourish here besides conditionals. We have these now **loops**. Recall that a loop is just something that does something again and again and again. Here, for instance, to Scratch how we might meow 3 times. In C there's going to be a few different ways to do this. Here is one using a **while loop**:

```c
int i = 3;
while (i > 0)
{
    printf("meow\n");
    i--;
}
```

You can declare a variable like `i` and set it equal to 3. You then use a `while` loop. If I start counting at 3, maybe I can just sort of decrement one at a time and get down to 0, at which point I can stop. This is going to have the effect of starting at 3, going to 2, going to 1, going to 0, and as soon as it goes to 0, this Boolean expression will no longer be true, and so the loop will just implicitly stop.

Alternatively, counting up from 0:

```c
int i = 0;
while (i < 3)
{
    printf("meow\n");
    i++;
}
```

And if you're a visual person, you can draw out what code looks like in flowchart form. You constantly have the condition being checked again and again — that's just how C works. As soon as I've incremented I from 0 to 1 to 2 to 3, 3 will no longer be less than 3, so the answer will be false, so the loop will just stop.

It turns out that looping some amount of times is so darn common that there's another alternative — a **for loop** — whose syntax is a little weird, a little harder to memorize, but it allows you to write slightly less code because you write more on a single line:

```c
for (int i = 0; i < 3; i++)
{
    printf("meow\n");
}
```

The way you read a for loop: you initialize the variable (everything to the left of this first semicolon), you then check the condition (`i < 3`), if so you execute what's inside of the curly braces, and then automatically the thing to the right of the second semicolon happens — `i` gets incremented. The condition is checked again — is 1 less than 3? It is, so we print meow again. And so on until the condition is false.

So it's exactly the same, but more magic is happening in this first line of code — you type fewer keystrokes and it feels a little nicer, a little tighter.

So let's go ahead and actually implement now this beginning of a cat in VS Code. Let me go back to VS Code and close `agree.c`. Let me reopen my terminal window and create an actual cat in `cat.c`. Let me do this initially the wrong way — copying and pasting `printf("meow\n");` three times. This is obviously wrong but it is correct if I want the cat to meow 3 times:

```c
#include <stdio.h>

int main(void)
{
    printf("meow\n");
    printf("meow\n");
    printf("meow\n");
}
```

But let's now use some of those new building blocks. With the while loop first:

```c
#include <stdio.h>

int main(void)
{
    int i = 3;
    while (i > 0)
    {
        printf("meow\n");
        i--;
    }
}
```

And then flipping it to count like a normal person from 0 up:

```c
int i = 0;
while (i < 3)
{
    printf("meow\n");
    i++;
}
```

The convention truthfully is in general in code to start counting from zero, start counting up to but not through the value you want. So at least you see the starting point and the ending point on the screen at the same time. But you can condense all of this a bit more and turn this whole thing into a for loop:

```c
for (int i = 0; i < 3; i++)
{
    printf("meow\n");
}
```

Now what could go wrong? Well, sometimes you might be inclined to do something forever, and indeed we did that in Scratch. You can achieve the same thing in code. In C we could use a while loop, but there is no "forever" block. Instead, if I want to do something forever I essentially need an expression here that's always true. The convention in programming is just to literally say `while (true)`:

```c
#include <cs50.h>
#include <stdio.h>

int main(void)
{
    while (true)
    {
        printf("meow\n");
    }
}
```

This would be an infinite deliberate loop. Let me go ahead and do `make cat` then `./cat`. This is like the annoying cat game — just meowing endlessly. Like I've now kind of lost control over my terminal window, and mark my words, at some point you might do this too. The answer to how to solve this is going to be **Control+C**. So there's a few cryptic keystrokes that you can use to generally interrupt things. Control+C would be our friend.

All right, so now that we've got control over our code space again, how can we go about making our meowing program a little more dynamic? Let's start asking the user how many times they want the cat to meow. I think we have all these building blocks thus far. So let me go ahead and stay in `cat.c` here and go ahead and delete the body of the contents of my main function. Let's give myself an `int` and I'll go ahead and call it `n` for number. I'm going to set it equal to the so-called return value of `get_int`, which is going to get an integer from the user:

```c
#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int n = get_int("How many? ");
    for (int i = 0; i < n; i++)
    {
        printf("meow\n");
    }
}
```

Now how can I use this variable? With a for loop, I could initialize a variable `i` for integer, set it equal to 0 initially. I could then do `i < n` — so I can use that variable as a placeholder inside of the loop — and on each iteration do `i++`. Back down to my terminal, `make cat`, `./cat`. I'm prompted this time for `n`. I can give it 3, and I'm going to get 3 meows. If I run it again with 4, I'm going to get 4 meows.

Now what is `get_int` doing for me? Well, it does a few things. For instance, suppose that instead of answering this question with a number, I say something random like "dog" — that is not an integer — and so the `get_int` function is designed to reject the user's input implicitly and just reprompt again, again and again. It does a kind of error checking for you, but it doesn't do everything. For example, an integer is a fairly broad category — it's like negative infinity through positive infinity. Suppose it makes no sense to ask the cat to meow -1 times, and yet the program accepts that.

So how can I begin to add some of my own error checking? Well, let me clear my terminal window and go back up into my code, and let me do something like this. After getting `n`, I can check if `n` is less than 0, and if so, I want to prompt the user again. But this leads to repetition — if I'm not careful I'll just keep copying and pasting the check. Really, to do this right we should prompt potentially as many times as it takes. So this is not the right path — we should use a loop.

For instance, using a **do-while loop**:

```c
#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int n;
    do
    {
        n = get_int("How many? ");
    }
    while (n < 0);

    for (int i = 0; i < n; i++)
    {
        printf("meow\n");
    }
}
```

You can literally say the word `do`, which means do the following, then you can do `n = get_int("How many? ")`, but then after those curly braces you use a `while` keyword — so at the end of the loop instead of the beginning — and that's where you put your Boolean expression. You can kind of invert the logic: do all of that while `n` is less than 0. This implicitly handles all of the continuation and all of the breaking — by just saying "do this while this is true." The difference between this do while loop and a normal while loop is literally that the condition is checked at the bottom instead of the top, so when you say `while (something)`, that question is asked first. Here the condition is only asked at the very end. And why is this useful? Well, oftentimes when writing programs where you want to do something at least once — like you obviously want to ask the user this question at least once — there's no point in checking while true first. You should just do it and then do it again if the expression evaluates to true.

---

## Functions

So let's actually make the software a little better designed. And to do this, we'll revisit an idea that we touched on last week having to do with problems — creating your own function. C does not come with everything you might want, and CS 50's library is not going to come with everything you might want. And at the end of the day, a lot of programming is about abstracting away your ideas — so you solve a problem once and then reuse it, reuse it, reuse it. And heck, you can package it up in a so-called library like we have and let other people use it as well.

So here, for instance, in Scratch is how we could have implemented the notion of meowing — as by getting the cat to play the sound "meow until done." We abstracted it away and then we had a magical new puzzle piece called "meow." In C, this is going to be a little weird today, but next week these details will start to make more sense. You would instead do the following — literally type `void`, the name of the function you want to create, and then `void` again in parentheses:

```c
void meow(void)
{
    printf("meow\n");
}
```

For now, know that this is the return value of the function. So `void` means it returns nothing. This is the input to or the arguments to the function — `void` means it takes no inputs. And that makes sense because literally "meow" doesn't return anything, it doesn't take anything, it just meows. It has a so-called side effect.

So this means: hey, C, invent a function called `meow` that takes no input, produces no output, but does have a side effect of printing "meow" on the screen.

Meanwhile, if I wanted to do something like this in code where I meow 3 times, well, I have the building blocks for this — and here's where inventing your own functions starts to get more compelling. I can abstract away the notion of meow. Now this doesn't come with C, it doesn't come with the CS 50 library. I just created this meow function, so I can call it with a for loop and call that new function meow 3 times.

But I can abstract this away further. I can edit the function to take an input — otherwise known as an argument — called `n`. And in C I can achieve the exact same thing:

```c
void meow(int n)
{
    for (int i = 0; i < n; i++)
    {
        printf("meow\n");
    }
}
```

This version does take an input, and just like before, when you create a variable in C, you specify the type and the name. When you invent your own function in C and it takes one or more inputs — AKA arguments — you specify the type and the name of those as well. No semicolons up there, just inside of the parentheses. But the rest of this code is exactly the same except instead of 3, I'm now using `n`.

So how can I go about implementing this myself? Well, let me go back to VS Code here and let me go ahead and let's really delete most of the code that I've written inside of main, and let me just suppose for the moment that meowing exists, and I'm going to go ahead and say:

```c
#include <stdio.h>

// Prototype
void meow(void);

int main(void)
{
    for (int i = 0; i < 3; i++)
    {
        meow();
    }
}

void meow(void)
{
    printf("meow\n");
}
```

Now if I scroll back up, you'll see there's no definition of meow yet at the top — so I'm going to invent that too. And much like last week where I sort of dramatically moved the meow definition way down to the bottom of the screen just to make the point that you don't need to see it anymore, out of sight out of mind — let me try to do the same here. Let me go way, way down and paste the meow function down there, then scroll back up. Out of sight, out of mind. I've already implemented the idea of meowing.

But there is a caveat in C. When I now clear my terminal and `make cat`, now I've introduced a problem — `cat.c` line 9, "call to undeclared function meow." Why is the compiler being kind of dumb here? Because C compilers are fairly simplistic — they won't proactively do you the favor of checking all the way down to the bottom of the file. They're going to take you literally. So if meow doesn't exist as of line 9, that's on you. That is an error.

I could fix this by just moving the meow function back up to the top, but let me argue that in general when writing C programs, the `main` function is literally meant to be the main part of your code. It kind of stands to reason that it should be at the top so that when you open the file, you see the main program that you care about. So there's an argument to be made for putting your custom functions below main.

The solution is the **prototype** — copy the first line of the function (its so-called signature) and put that one line and only that one line with a semicolon above main. This is what's known as a prototype — a bit of a hint to the compiler, a promise if you will: "hey, compiler, there will exist a function called `meow`, it takes no input and it returns no output, semicolon, and it's on the honor system that it will eventually exist later in the file."

What I've done here on line 4 as an aside is what's generally known as a **comment**. Anything in C that starts with `//` is a note to self — a sticky note — which is just for the human, not for the computer. It's a way of reminding yourself or someone else what's going on.

Now if I go back into my terminal and clear those errors, `make cat` again — now it does work because the meow function has been defined exactly where it should be.

Now I can make the new version even better. I could change the function `meow` to take a variable `n` as input for the number of times, and then in here I could do something like my for loop:

```c
void meow(int times)
{
    for (int i = 0; i < times; i++)
    {
        printf("meow\n");
    }
}
```

And now inside main, I'm going to ask the user how many times:

```c
int main(void)
{
    int n = get_int("How many? ");
    meow(n);
}
```

I need to update the prototype too: `void meow(int times);`. And I pass in the variable `n`, but in the context of the meow function, that same variable is referred to as `times` because you're passing it in as input and giving it its own name — and that's totally your prerogative. It's just a matter of scope. I could have called it `m` or some other letter of the alphabet, but `times` is even more clear because that's the number of times I want the cat to meow.

All right, let me add one other feature to this to demonstrate that we can take not only input but actually produce output if we want. If I want a function that returns an integer rather than having a `void` return type, I can make a function like `get_positive_int`:

```c
int get_positive_int(void)
{
    int n;
    do
    {
        n = get_int("How many? ");
    }
    while (n < 0);
    return n;
}
```

Notice this notion of **returning a value** is new here. This is consistent with the hint on the function's first line which implies that this `get_positive_int` function is going to return not `void` but an integer — and that's the whole purpose of this function in life. If I now use this in main:

```c
int main(void)
{
    int n = get_positive_int();
    meow(n);
}
```

I need to add its prototype above main too. And I have this sort of abstraction here of a function whose whole sole purpose in life is to get me not just an integer, but one that is zero or positive and not negative.

---

## Correctness, Design, Style

All right, so let's take a higher level look now at some of the things we've been thinking about. So when it comes to writing good code, CS 50 and really the world in general tends to focus on these kinds of axes: **correctness**, **design**, and **style**.

**Correctness** just means does the code work the way it's supposed to? In the context of a class, it should do exactly what the homework assignment — AKA problem set — tells you to do. In the real world, it should do exactly what someone decided the software should do — the product manager, the CEO, or the like. Correctness just means it behaves as it should.

That's different though from how well **designed** the code might be, and we've seen that a few times. I've had some simplistic examples in Scratch and C that were 100% correct, like they did the right thing logically, but I was wasting the computer's time, wasting the human's time by asking more Boolean expressions than I needed to and so forth. So design is more about — in the English analogy — not only saying things that are correct but doing it well, making a good cogent argument, not just one that happens to be correct.

**Style** meanwhile is the third axis on which we might evaluate the quality of someone's code, and that's more of the aesthetics — like is everything pretty printed, that is nicely indented? Are variables well named and not just called X, Y, Z arbitrarily or something like that? So style matters really to other humans, not to the computer, but to other humans.

And to illustrate these — you'll see that in problem set one onward you'll be given a number of tools that you can use. One of those tools is called **check50**, and in each problem in C and Python and other languages, you'll be showed how you can test your own code — you can literally run a command that CS50 created called `check50`. You'll then specify what's called a slug, which just means a unique identifier for that homework problem, and you'll get quick feedback on whether or not your code is correct.

Design though is much more subjective. **design50** is built on top of the CS50 duck, whereby if you have a program open in a tab, you click design50, you will get chatGPT-like advice on how you can improve not the correctness of that code, but the design of that code, the quality thereof.

**style50** meanwhile is a third tool that will provide you with feedback on the style of your code. It will show you on the left what your code looks like and on the right what your code really should look like, insofar as it should be consistent with what we've taught in class and consistent with CS 50's so-called style guide.

So correctness, design, style is not only how we, but really the world writ large, tends to evaluate the quality of code.

---

## Mario

All right, as you walked in, we had a little walkthrough of Super Mario Brothers playing from yesteryear, which was a side-scrolling game in which Mario would jump and go up, down, left, right and try to collect coins and make it to the end of the level. We're not going to do anything graphical just yet — we're leaving graphics behind for now in the form of Scratch — but with C we can implement some of these ideas.

For instance, if I were to write code to generate just this row of 4 question marks, I dare say there's a bunch of ways we can do this. Let's see if we can't use all of today's building blocks to start implementing our own tiny version of Super Mario Brothers in a file, say, called `mario.c`.

So let me open and clear my terminal window. Let me run `code mario.c`. And let's just try to do something super simple like print 4 question marks in a row. The simplest possible implementation:

```c
#include <stdio.h>

int main(void)
{
    printf("????\n");
}
```

Now I'm kind of cheating here by just hard coding 4 question marks. What if I wanted not 4 but 3 or 5 or some other number? Well, we could do that with a loop too. So let me change this code here:

```c
for (int i = 0; i < 4; i++)
{
    printf("?");
}
printf("\n");
```

Now I've got a loop printing one question mark at a time, and after the loop finishes I print a newline. If I put the `\n` inside the loop I'd get a column instead of a row — I foolishly included the backslash N after each question mark, and that gave me a column. So I put the `\n` outside of the loop so once I'm done printing all of the question marks, then I get the newline. Now if I do `make mario` and `./mario`, I get the 4 question marks in a row plus a new line.

Let's try another. In Super Mario Brothers, when you go into the underground world, you see a column of bricks that he has to jump over. So those here — how might we make a column?

```c
for (int i = 0; i < 3; i++)
{
    printf("#\n");
}
```

`make mario` `./mario`. OK, now we're back in business. But let's make it more interesting by going into Mario's underground — here's the third and final Mario problem whereby we want to implement a 3 by 3 grid of bricks. This one's interesting because we've never done something in two dimensions. I did horizontal, I did vertical, but we haven't really composed those ideas into the same.

So let me now think a little harder about how I can print out row, row, row. And this is where if you have in your mind's eye any familiarity with old-school typewriters — it's kind of the same idea where you want to print a row of bricks, then go back to the beginning, a row of bricks, then go back to the beginning, and a row of bricks. And that's kind of what `printf` has always been doing for us — it's printing line by line by line of text.

Let me go into my main function here. And if I want to print out something two-dimensional, let me kind of think about it as rows and columns. So maybe:

```c
for (int row = 0; row < 3; row++)
{
    for (int col = 0; col < 3; col++)
    {
        printf("#");
    }
    printf("\n");
}
```

This is my "for each row" outer loop, and "for each column" inner loop. It's totally fine to nest loops in this way. But I probably don't want the inner loop's variable competing with the outer loop's variable by giving them the same name. And that's fine — it is pretty conventional in code when you want another integer and you've used `i` already, you can use `j`. So using `i` and `j` and `k` is generally fine.

Now what's really happening here? The outer loop handles row by row by row, but each time you're on a row you first want to do column, column, column — and that's what logically the nesting is achieving. `make mario` `./mario` — now we've got the 3x3 grid. The takeaway here being you can certainly nest these kinds of ideas and compose them.

Now this is a little more subtle, but there is a bit of duplication in this program. Anyone want to conjecture what still could be improved here? Yeah — I've hard coded the 3 here and here. It's not a big deal for an in-class exercise, but if I want to make this square bigger and bigger over time, I'm going to have to change it in two different places, and that's just bad design. So how could we fix this?

```c
const int n = 3;

for (int row = 0; row < n; row++)
{
    for (int col = 0; col < n; col++)
    {
        printf("#");
    }
    printf("\n");
}
```

We could just declare a variable like `n`, set it equal to 3, and then use `n` in both places. But we can do one better than this — it turns out in C and in many languages there's the notion of a **constant**, whereby if you want to store something in a variable but you want to signal to the compiler that this value should never change — and better still, you want to prevent yourself or a colleague from accidentally changing this value — you can declare it to be `const`:

```c
const int n = 3;
```

If I do something stupid later in my code and I try to set `n` equal to something else, the compiler won't let me do that. It will protect me from myself — so it's just a slightly better design as well.

---

## Operators

All right, let's focus lastly on things we can't really do well with computers, namely some of the limitations thereof. So here is a cheat sheet of some of the operators we've seen thus far:

- `+` — addition
- `-` — subtraction
- `*` — multiplication
- `/` — division
- `%` — modulo (the remainder operator)

Let's use some of these to make our own calculator and see what this calculator can and can't do for us. So back here in VS Code, let me open my terminal. Let's go ahead and create a program called `calculator.c`. Let me include `cs50.h` and `stdio.h`, copy paste our usual `int main(void)`, and inside of main:

```c
#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int x = get_int("What's x? ");
    int y = get_int("What's y? ");
    printf("%i\n", x + y);
}
```

`make calculator` `./calculator` — what's X is 1, what's Y is 2, and indeed I get 3. So not a bad calculator. It seems to be working correctly. But it's maybe not the best design — it's generally frowned upon to create a variable like `z` if you're only going to use it a moment later in one place. So I can just do `x + y` right there in the `printf`. That's totally fine and reasonable.

Let's do something like this — not just addition. Why don't we use some multiplication:

```c
int x = get_int("What's x? ");
printf("%i\n", x * 2);
```

Let me make this version of the calculator — `./calculator`. Let's do 1: 1 times 2 is 2. Let's do 22: times 2 is 4. Let's do 33: times 2 is 6, and so forth. That's fine. It seems to work.

But maybe let's implement a recent meme. Let me do something like this:

```c
#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int dollars = 1;
    while (true)
    {
        char c = get_char("Here's $%i. Double it and give to next person? ", dollars);
        if (c == 'y')
        {
            dollars *= 2;
        }
        else
        {
            break;
        }
    }
}
```

`make calculator` `./calculator` — "Here's $1. Double it and give to the next person?" OK, Y. "Here's $2." OK. OK. OK. I'm going to do it faster. It's getting pretty high. Let's keep going... And that does not happen in the memes. What happened here? Exactly — good intuition. Because the computer only has a finite number of bits allocated to each integer. I hypothesized earlier that it's usually 32 bits, maybe 64 bits, but it's finite. So you can only count so high — it's roughly 4 billion, or again an integer by default can be negative or positive, so it's roughly 2 billion, and that's pretty close to what we were getting here.

In fact, we **overflowed** the integer in memory. **Integer overflow** is a term of art whereby you can overflow an integer by trying to store too big of a value in it, and the reason for this is again that this is a piece of memory inside of a laptop or a desktop or some other device — in these little chips is a whole bunch of bits or really bytes that can store information electronically, but they allocate those bits in units of 8, maybe 16, maybe 32, maybe 64, but finitely many per value.

As a small scale example: if we have a 3 digit number as represented by 3 physical light bulbs or 3 tiny transistors in the computer, I can count from 0 to 1 to 2 to 3 to 4 to 5 to 6 to 7. If I want to count to 8 though, I need a 4th bit. But if you don't have a 4th bit, for all intents and purposes, that number is just 0. Or as an aside, depending on how you're representing your numbers, sometimes a leading one indicates that the number itself is negative, which is why in VS Code we actually saw both symptoms — first we went negative because we wrapped around logically, and then we did indeed end up on 0 ultimately.

How can we chip away at this? Well, a couple of solutions perhaps. Let me close my terminal window here and instead of using an `int`, well, let's just kick the can down the road — let's use a `long`, which is 64 bits. So at least we can give away even more money in this scenario. I can't use `%i` — I need to use `%li` now for a long integer.

But the same problem eventually happened again — we overflowed this long integer, even using that many bits, because exponentiation works fast and I kept hitting Y enough times to overflow even the long integer. So that too was a problem, and this happens truly in the real world.

Picture here is a Boeing 787 from a few years back, whereby after 248 days of continuous power — the New York Times reported a few years back that a Model 787 airplane that has been powered continuously for 248 days can lose all alternating current electrical power due to the generator control unit simultaneously going into fail-safe mode. This condition is caused by a **software counter internal to the GCUs that will overflow** after 248 days of continuous power. Boeing is in the process at the time of developing a GCU software upgrade that will remedy the unsafe condition.

So literally what this means is that the power to these planes would just shut off if the planes were on for more than 248 days at a time. The short-term fix was what? Literally turn it off and back on again — much like you've probably been taught with your phones and computers and any other electronic devices that somehow freak out on occasion. Reboot the plane. Any time you reboot a phone or a laptop or a plane, all of those variables get reset to their default values. So this effectively solved the problem. But when they finally rolled out a fix, then you didn't have to do that anymore. The source of the problem is essentially that they were probably using 32-bit integers — with a signed integer, so they had 31 bits at their disposal to count positive numbers — and 248 days is roughly how many tens of a second there are.

There's a historical bug in Pac-Man whereby you can play up to level 255, but because there was a missing if condition that checked what level you were on, you could accidentally garble the screen if you were amazing at Pac-Man because they too would overflow an integer and random characters would end up appearing on the screen. So it's sort of like a badge of honor to actually hit level 256 in this way because of this bug.

But there's yet other issues we can see here. If I were to revamp my calculator as follows — clear my terminal window, get rid of all of this meme code, and just do something like:

```c
#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int x = get_int("What's x? ");
    int y = get_int("What's y? ");
    printf("%i\n", x / y);
}
```

`make calculator` `./calculator`, type in 1, type in 3. I get 0, which is weird. What if I do instead maybe 2 and 3? It's 0 instead of 0.66. What if I do 3 and 3? Well, that curiously works. But if I do something like 4 and 3, which would be 1.33, that doesn't seem to work either.

So there's this other issue in computing when you have finite numbers of bits known as **truncation**, whereby even when you're trying to do floating point math like with a decimal point, if you are using an integer, you're going to throw away everything after the decimal point unless you're explicitly using the right data type. If I actually go in now and change my values from integers to floats and change `%i` to `%f` and remake this calculator:

```c
float x = get_float("What's x? ");
float y = get_float("What's y? ");
printf("%f\n", x / y);
```

Now I can do 1 divided by 3 and I actually get that response. But there's another issue latent here. I'm going to tweak the `%f` to be a little arcane — it turns out you can specify how many significant digits you want to show by using a dot and then a number like 50 arbitrarily:

```c
printf("%.50f\n", x / y);
```

And contrary to what you might have learned in grade school, this calculator would seem to think that 1 divided by 3 is not 0.33333333 infinitely many times — there's all this random stuff happening at the end. Long story short, this is because computers only use finitely many bits even to represent floating point numbers, and if there's an infinite number of those, you can't possibly represent every possible floating point value. So we're essentially seeing an approximation of 1/3. This too happens quite a bit in the wild. There's really no solution to this other than throwing more bits at the problem using a `double` instead of a `float`, or at least somehow trying to detect this and catch this. That then is what we'd call **floating point imprecision**.

---

## Summing Up

But to tie this together and sort of induce a bit of fear for the coming years — these things happen all of the time. Back when I was finishing school, there was the so-called **Y2K problem** or year 2000 problem, whereby for decades computers had been using not 4 digits to represent years but just two, because it was convenient and more efficient since you use half as much memory. Of course when the year rolled around from 1999 to 2000, if you didn't have these extra numbers in memory, you might confuse 2000 with 1900 — which was the presumption if you're only storing two digits. So we screwed that up, and thankfully the world scrambled, and if you read up on Wikipedia and news articles from the time, everyone thought the world might very well end, but it didn't.

You'd think we'd learned our lesson. Unfortunately, another such problem is coming up in the year **2038**, whereby historically since the 70s and prior, computers have generally used 32-bit integers to keep track of time — the date and the time — by means of counting how many seconds have passed since January 1st, 1970, and all of the math is just relative to that date because that's when computers were really starting to come onto the scene. Unfortunately, there's only 4 billion values you can count to — or 2 billion if you're doing negatives — from January 1st, 1970. And so on the date January 19th, 2038, we will overflow a 32-bit counter and suddenly if this problem is not fixed by you or other people before the year 2038, our computers and phones and other devices may very well think it's December 13th, 1901.

So there are solutions to these problems. CS 50 is all about empowering you with solutions to these problems. But that though is week one for CS 50. Problem set one will be in your hands soon. We'll see you next time.

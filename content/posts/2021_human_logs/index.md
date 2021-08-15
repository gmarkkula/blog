---
title: On fruit and human logarithms
date: 2021-02-01T07:31:59Z
draft: true
---

*Regardless of how much or little maths you know or do, you have probably at least heard about logarithms, perhaps especially in the context of the "logarithmic scale" which is sometimes used to show data in graphs, for example to track the growth of a pandemic. In my job I use logarithms quite a lot, but there is still something slightly baffling about them, so I thought I'd devote this post to logarithms: what they are in terms of a general maths tool, but also how they - interestingly - turn up in human behaviour sometimes. In what ways, and why?*

Perhaps the easiest way to intuitively think about what a logarithm is, is that it is the opposite (or "inverse") of exponential growth. And by exponential growth I mean the kind of growth you get when you have a number of something, for example a number of people infected with a disease, and that number gets repeatedly scaled up by the same multiplication over and over, for example because each infected person infects a number of other people within a certain time, and then the same thing happens again and again. This pandemic example is only a little too familiar though, so let's switch to a nicer one: the number of branches or fruits in a tree, like the one below. Click/touch in the image to toggle fast forward, do a long press to get a new tree. 

(interactive tree growth animation)

In the animation above, each new branch gives rise to about three smaller branches, each smaller branch in turn giving rise to about three even smaller branches, and so on. So after one branching step, there are about three branches, after two branching steps 3 x 3 = 9 branches, then 3 x 3 x 3 = 27, then 81, 243, 729, and so on. Repeated upscaling by the same multiplication, in other words exponential growth. Or not quite. In practice I have limited the maximum number of branching steps in the animation, to not have your computer crash from having to draw so much stuff on your screen. Because of course, a hallmark of exponential growth is that it quickly explodes out of control:

(interactive exponential growth curve, number of branches as a function of branching steps)

And the corresponding hallmark of the logarithm, then, is that it brings this explosion back in check, by effectively instead just telling you how long the growth has been going on, which tends to be a more manageable number. Specifically, if you take the number of branches in the tree and you apply the logarithm to that number, then you get back the number of branching steps since the tree started growing. So the logarithm of 3 is one, the logarithm of 9 is two, and the logarithms of 27, 81, 243, 729, are three, four, five, and six. Here it is, as a graph - and the curve to the right is the logarithm.

(interactive exp log mirror plot)

Note that the graph on the bottom is the same as the one above it, just shown in a logarithmic scale instead. What this means in practice is that a value y is drawn not at a height y over the zero line, as in a normal plot, but instead at a height that is the logarithm of the value y. And since the curve we are showing above is a pure exponential growth, it comes back looking as a completely straight line in this logarithmic scale plot. A second thing to note is the little "3" in the $\log_3$

Humans make logarithms... Hicks studied speed of stimulus-response mappings ...

(Hicks 1952 plot)

Play the game below... score based on how good you are compared to the function Hicks found in 1952...

(Hicks fruit game)

But sensitive to exact task... cheat in game above...

Breaks the logarithm... Interestingly, there is still another logarithm at work here, in how quickly you are able to reach for the target location, as a function of how big it is and far away... A post for another day...

So why is there a logarithm here...? Hicks had his own thoughts about this... couched in terms of information theory which was really new and hot at the time... Title of the paper: "On the rate of gain of information"... in bits... One or zero... If you are specifying a higher number you need a larger number of bits... And how does the number of bits you need grow with the number of you want to specify? Logarithmically. And the reason for this is that again we get back to the idea of a tree...

(interactive tree plot - height chosen by mouse Y, target fruit chosen by mouse X)

So Hicks suggestion was that the brain is dealing with this decision situation by way of a kind of divide and conquer, iteratively dividing the search space for the right response into smaller and smaller parts. Intuitively, in the fruit game, this could be something like.... "I know the banana is in the right half... I know that it is in the lower part of the right half" ... And the fewer target locations you have to choose from, the quicker there will only be one location left, which will then be the right answer. So the "rate of gain of information" can be thought of as "how quick is the brain at iteratively dividing the search space?"...

So is the brain really doing something like this? That is a big and interesting question, and has been tackled by a lot of people in different ways... Somewhat of a benchmark for models of how the brain solves this type of decision challenge... Again a topic for a different post...


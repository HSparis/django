from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from PIL import Image, ImageDraw

from blog.models import Category, Post, Tag
from django.contrib.auth import get_user_model


POSTS = (
    {
        "title": "Why the Sea of Japan Shapes Life in Niigata",
        "slug": "sea-of-japan-life-in-niigata",
        "category": "Culture",
        "tags": ("Niigata", "Japan", "Travel"),
        "art": "waves",
        "colors": ("#102c42", "#197a87", "#f0b66f"),
        "content": (
            "Niigata is often introduced through its rice, but its relationship with "
            "the Sea of Japan is just as important. The coast has long connected "
            "communities to fishing, trade, and travel. It also gives the region a "
            "distinct rhythm: sea breezes, changing skies, and a horizon that feels "
            "very different from the crowded streets of a major city.\n\n"
            "That connection is easy to notice in the food. Seasonal seafood appears "
            "alongside local rice, and many neighborhood restaurants keep their menus "
            "close to what is available. A good meal here can tell a small story about "
            "weather, geography, and the people who work along the coast.\n\n"
            "Visitors do not need a complicated itinerary to experience this side of "
            "Niigata. Take time for a walk near the water, try a seasonal dish, and "
            "watch how the light changes in the afternoon. The most memorable "
            "discoveries are often the unplanned ones: a quiet view, a friendly shop, "
            "or a local specialty you had never heard of before."
        ),
    },
    {
        "title": "A First-Timer's Guide to Niigata City Beyond Tokyo",
        "slug": "first-timers-guide-niigata-city",
        "category": "Travel",
        "tags": ("Niigata", "Japan", "Travel"),
        "art": "mountains",
        "colors": ("#26394c", "#577e82", "#efbd78"),
        "content": (
            "Japan is much more than its best-known destinations. Niigata City makes "
            "a rewarding first stop for travelers who want a slower pace without "
            "giving up the comforts of a well-connected city. Its neighborhoods, "
            "river views, food culture, and access to the wider region offer plenty "
            "to explore over a relaxed weekend.\n\n"
            "Start with a walk rather than trying to see everything at once. The "
            "Shinano River and the waterfront provide a sense of the city's scale, "
            "while shopping streets and small cafes offer an everyday view of local "
            "life. Leave room in your schedule for a market or a meal chosen by "
            "curiosity instead of a checklist.\n\n"
            "A few practical habits make the trip smoother: carry some cash for "
            "smaller businesses, check local transit times before heading out, and "
            "keep a flexible plan in case the weather changes. Most of all, treat "
            "Niigata as a destination in its own right. Slowing down is not a gap in "
            "the itinerary; it is part of what makes the visit worthwhile."
        ),
    },
    {
        "title": "The Quiet Art of Japan's Seasonal Festivals",
        "slug": "quiet-art-japanese-seasonal-festivals",
        "category": "Culture",
        "tags": ("Culture", "Japan", "Traditions"),
        "art": "lanterns",
        "colors": ("#382a46", "#a44953", "#f0c27a"),
        "content": (
            "Japanese festivals are often remembered for their music, food stalls, "
            "and bright decorations. Yet many of their most meaningful moments are "
            "quiet ones: a lantern being lit, a neighborhood preparing together, or "
            "families returning to a familiar place at the same time each year.\n\n"
            "Seasonal celebrations connect daily life with the calendar. They make "
            "the changing year visible through local customs, regional foods, and "
            "shared routines. The details vary from one community to another, which "
            "is why a small neighborhood event can feel just as distinctive as a "
            "large, well-known festival.\n\n"
            "For visitors, the best approach is to take part with curiosity and "
            "respect. Follow local guidance, be mindful when taking photographs, "
            "and remember that many events are community gatherings rather than "
            "performances staged for tourists. A little patience can reveal the "
            "care behind the celebration and the people who keep it alive."
        ),
    },
    {
        "title": "How Japanese Convenience Stores Became Everyday Infrastructure",
        "slug": "japanese-convenience-stores-everyday-infrastructure",
        "category": "Technology",
        "tags": ("Japan", "Everyday Life", "Technology"),
        "art": "store",
        "colors": ("#1c3850", "#267e83", "#f0c66d"),
        "content": (
            "A Japanese convenience store is more than a place to grab a snack. "
            "For many people, it is a dependable part of the neighborhood: somewhere "
            "to pick up a quick meal, handle a small errand, or find basic necessities "
            "at almost any hour. Its usefulness comes from a collection of thoughtful "
            "services rather than one dramatic invention.\n\n"
            "The experience is shaped by careful operations. Shelves are replenished "
            "frequently, seasonal products keep the selection fresh, and clear "
            "packaging helps customers make quick choices. Some stores also provide "
            "services such as bill payment, parcel handling, and ticket printing, "
            "bringing everyday tasks into one accessible location.\n\n"
            "There is a design lesson here for technology teams: convenience is built "
            "from reliability, good timing, and a clear understanding of what people "
            "actually need. A service does not have to be flashy to become essential. "
            "When small interactions work consistently, they earn a place in daily "
            "life."
        ),
    },
    {
        "title": "What Cozy Games Can Teach Us About Thoughtful Design",
        "slug": "cozy-games-thoughtful-design",
        "category": "Games",
        "tags": ("Games", "Game Design", "Indie Games"),
        "art": "gamepad",
        "colors": ("#253a55", "#4d8790", "#efc27d"),
        "content": (
            "A cozy game is not simply a game without conflict. Its appeal often "
            "comes from giving players room to set their own pace, notice small "
            "details, and feel that their actions matter. Gardening, arranging a "
            "space, helping a character, or collecting objects can become satisfying "
            "when the game makes each step feel considered.\n\n"
            "Good cozy design respects attention. It explains its systems clearly, "
            "offers welcoming feedback, and avoids turning every activity into a "
            "timer or a competition. A gentle soundtrack, readable menus, and "
            "consistent visual cues all help players settle into the experience "
            "without demanding constant urgency.\n\n"
            "These ideas are useful well beyond cozy games. Any interactive product "
            "can benefit from making progress visible and giving people control over "
            "how they engage. Calm does not mean empty; it means the experience has "
            "space for curiosity. The strongest relaxing games understand that "
            "small rewards can create a lasting connection."
        ),
    },
    {
        "title": "A Beginner's Guide to the Worlds of Japanese RPGs",
        "slug": "beginner-guide-japanese-rpg-worlds",
        "category": "Games",
        "tags": ("Games", "JRPG", "Game Design"),
        "art": "portal",
        "colors": ("#242a55", "#6559a0", "#f1c578"),
        "content": (
            "Japanese role-playing games, often called JRPGs, cover a broad range of "
            "styles. Some focus on turn-based battles and carefully planned teams; "
            "others build their stories around exploration, action, or relationships "
            "between characters. The label is a useful starting point, not a rulebook "
            "that every game must follow.\n\n"
            "If you are new to the genre, choose a game whose setting interests you "
            "and give its opening a little time. Many RPGs introduce their worlds "
            "gradually, teaching combat and story systems through early chapters. "
            "There is no need to master every optional feature before enjoying the "
            "main adventure. Start with the basic tools, then explore deeper systems "
            "when they become fun rather than obligatory.\n\n"
            "What makes the genre memorable is often the combination of a journey "
            "and a cast of characters who change along the way. Whether the story is "
            "large and fantastical or intimate and grounded, the best entry point is "
            "the one that makes you want to see what happens next."
        ),
    },
    {
        "title": "Why Arcades Still Matter in Japan's Gaming Culture",
        "slug": "arcades-japan-gaming-culture",
        "category": "Games",
        "tags": ("Games", "Arcades", "Japan"),
        "art": "arcade",
        "colors": ("#20233f", "#8c4274", "#f3c86c"),
        "content": (
            "An arcade offers something a home console cannot quite reproduce: "
            "a shared room full of games, sounds, and people. Players can watch a "
            "match, take turns, compare scores, or discover a machine they had not "
            "planned to try. The space itself becomes part of the entertainment.\n\n"
            "Japanese arcades have also made room for many kinds of play. Rhythm "
            "games reward timing and practice, crane games turn a few seconds into "
            "a small challenge, and competitive cabinets invite players to improve "
            "through repeated matches. The variety makes an arcade interesting "
            "even when you arrive without a specific game in mind.\n\n"
            "For travelers, an arcade visit can be a low-pressure way to experience "
            "a different side of gaming culture. Be considerate of other players, "
            "check how a machine works before starting, and enjoy the atmosphere as "
            "much as the score. The appeal is not only nostalgia; it is the energy "
            "of playing alongside other people."
        ),
    },
    {
        "title": "The Craft Behind Japanese Independent Games",
        "slug": "craft-behind-japanese-independent-games",
        "category": "Games",
        "tags": ("Games", "Indie Games", "Japan"),
        "art": "pixels",
        "colors": ("#233747", "#527d67", "#efc27c"),
        "content": (
            "Independent games are often made by small teams working with limited "
            "time and resources. That constraint can encourage a clear creative "
            "identity: a distinctive visual style, a focused mechanic, or a story "
            "that would be difficult to stretch across a much larger production.\n\n"
            "Japan's indie scene is diverse, with developers drawing on personal "
            "interests, local communities, and global influences. Some projects "
            "revisit familiar genres with a fresh perspective, while others build "
            "their entire experience around one unusual idea. Tools for publishing "
            "digitally have also made it easier for small teams to reach players "
            "outside their home region.\n\n"
            "When exploring indie releases, look beyond the first screenshot. "
            "Developer notes, short demos, and interviews can help explain what "
            "makes a project special. Supporting a small studio does not always "
            "mean buying every game you see: sharing a thoughtful review or "
            "recommending a title to a friend can help its audience grow too."
        ),
    },
    {
        "title": "Small Technology, Big Impact in Everyday Japan",
        "slug": "small-technology-everyday-japan",
        "category": "Technology",
        "tags": ("Technology", "Japan", "Everyday Life"),
        "art": "circuits",
        "colors": ("#183744", "#287d79", "#e9bc70"),
        "content": (
            "Technology does not always announce itself with a screen or a new "
            "device. Sometimes its greatest value is a small improvement that "
            "removes friction from an ordinary task: a clear transit display, a "
            "well-designed payment terminal, or a public service that is easy to "
            "understand the first time you use it.\n\n"
            "Japan's cities offer many examples of technology working alongside "
            "physical spaces. Signs, machines, and mobile services can help people "
            "navigate busy stations and complete routine errands. The most effective "
            "systems account for more than speed: they also need legible information, "
            "accessible alternatives, and graceful ways to recover when something "
            "does not go as planned.\n\n"
            "For builders, the takeaway is to study the whole experience instead of "
            "focusing only on the newest feature. Ask where people hesitate, what "
            "information they need, and how the service behaves under everyday "
            "conditions. Useful innovation often feels simple because someone has "
            "done the hard work of making complexity manageable."
        ),
    },
    {
        "title": "Designing for Calm: Lessons from Japanese Interfaces",
        "slug": "designing-for-calm-japanese-interfaces",
        "category": "Technology",
        "tags": ("Design", "Technology", "Japan"),
        "art": "phone",
        "colors": ("#29364c", "#66848c", "#f0c47d"),
        "content": (
            "A calm interface is not defined by a particular color palette or "
            "minimal layout. It is an experience in which people can understand "
            "their choices, find the next step, and recover from mistakes without "
            "feeling rushed. Visual quiet is useful only when the information remains "
            "clear.\n\n"
            "Looking at interfaces used in Japan can prompt good questions about "
            "context. Who is using the service, where are they, and what do they "
            "need to do next? A station kiosk, a shopping app, and a personal "
            "finance tool have different constraints. Strong design responds to "
            "those conditions rather than applying one fashionable style everywhere.\n\n"
            "A practical way to improve a product is to remove uncertainty one "
            "interaction at a time. Use familiar language, make important actions "
            "easy to locate, and give feedback that explains what just happened. "
            "When a design respects attention, people can focus on their goal instead "
            "of learning the interface."
        ),
    },
)


def create_cover(art, colors):
    image = Image.new("RGB", (1200, 800), colors[0])
    draw = ImageDraw.Draw(image)
    top = tuple(int(colors[0][index:index + 2], 16) for index in (1, 3, 5))
    bottom = tuple(int(colors[1][index:index + 2], 16) for index in (1, 3, 5))

    for y in range(image.height):
        ratio = y / (image.height - 1)
        color = tuple(round(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3))
        draw.line((0, y, image.width, y), fill=color)

    accent = colors[2]
    draw.ellipse((770, 70, 1060, 360), fill=accent)
    draw.ellipse((810, 110, 1020, 320), fill=colors[1])

    if art == "waves":
        for y in range(360, 760, 65):
            draw.arc((80, y - 90, 1130, y + 90), 190, 350, fill=accent, width=8)
    elif art == "mountains":
        draw.polygon(((0, 610), (280, 280), (520, 610), (760, 330), (1200, 700), (1200, 800), (0, 800)), fill="#263b50")
        draw.polygon(((280, 280), (205, 370), (305, 345), (365, 390)), fill="#f1e4cc")
    elif art == "lanterns":
        for x, y in ((230, 270), (470, 420), (850, 460), (1040, 275)):
            draw.line((x, 70, x, y), fill="#f2dcae", width=5)
            draw.rounded_rectangle((x - 48, y, x + 48, y + 140), radius=24, fill=accent)
            draw.line((x - 34, y + 45, x + 34, y + 45), fill="#ffe7b0", width=5)
    elif art == "store":
        draw.rectangle((150, 400, 1030, 760), fill="#e9e0ca")
        draw.rectangle((190, 355, 990, 470), fill=accent)
        draw.rectangle((240, 500, 480, 760), fill="#2b3b50")
        draw.rectangle((535, 510, 950, 635), fill="#c6d8c9")
        for x in (570, 690, 810):
            draw.rectangle((x, 535, x + 70, 610), fill="#e7a35f")
    elif art == "gamepad":
        draw.rounded_rectangle((220, 390, 980, 650), radius=110, fill="#eee5d0")
        draw.rounded_rectangle((320, 445, 460, 590), radius=22, fill="#34445d")
        draw.rectangle((375, 465, 405, 570), fill=accent)
        draw.rectangle((337, 503, 443, 533), fill=accent)
        for x, y in ((735, 485), (815, 550), (875, 465), (775, 590)):
            draw.ellipse((x, y, x + 38, y + 38), fill=colors[1])
    elif art == "portal":
        draw.ellipse((350, 240, 850, 740), outline=accent, width=38)
        draw.ellipse((425, 315, 775, 665), outline="#eee1c8", width=12)
        draw.polygon(((0, 760), (380, 570), (730, 760)), fill="#34375f")
        draw.polygon(((650, 760), (950, 520), (1200, 760)), fill="#45436f")
    elif art == "arcade":
        for x, height in ((100, 250), (330, 360), (560, 300), (790, 410), (1020, 280)):
            cabinet_top = 690 - height
            draw.rounded_rectangle((x, cabinet_top, x + 150, 700), radius=18, fill="#eee3cb")
            draw.rectangle((x + 20, cabinet_top + 35, x + 130, cabinet_top + 130), fill=accent)
            draw.ellipse((x + 55, cabinet_top + 150, x + 95, cabinet_top + 190), fill="#f4d996")
    elif art == "pixels":
        for row in range(5):
            for column in range(7):
                if (row + column) % 3 != 0:
                    x, y = 230 + column * 105, 365 + row * 70
                    draw.rectangle((x, y, x + 65, y + 45), fill=accent if row % 2 else "#e6dfc8")
    elif art == "circuits":
        for x in range(170, 1100, 190):
            draw.line((x, 320, x, 690), fill=accent, width=8)
            draw.line((x, 430, min(x + 145, 1160), 430), fill=accent, width=8)
            draw.ellipse((x - 20, 300, x + 20, 340), fill="#f3e5c9")
            draw.ellipse((min(x + 125, 1140), 410, min(x + 165, 1180), 450), fill="#f3e5c9")
    elif art == "phone":
        draw.rounded_rectangle((405, 190, 795, 740), radius=50, fill="#eee7d8")
        draw.rounded_rectangle((435, 240, 765, 660), radius=20, fill="#526f78")
        draw.rounded_rectangle((480, 300, 720, 350), radius=12, fill=accent)
        draw.rounded_rectangle((480, 390, 680, 420), radius=12, fill="#d8d8c8")
        draw.rounded_rectangle((480, 450, 700, 480), radius=12, fill="#d8d8c8")
        draw.ellipse((570, 685, 630, 745), fill="#526f78")

    output = BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()


class Command(BaseCommand):
    help = "Create ten original Neo Niigata sample articles with locally generated covers."

    def add_arguments(self, parser):
        parser.add_argument(
            "--author",
            required=True,
            help="Username of the existing account that should own the sample posts.",
        )

    @transaction.atomic
    def handle(self, **options):
        username = options["author"]
        try:
            author = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist as exc:
            raise CommandError(f"No user found with username {username!r}.") from exc

        created_count = 0
        for data in POSTS:
            category, _ = Category.objects.get_or_create(name=data["category"])
            post, created = Post.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "author": author,
                    "title": data["title"],
                    "content": data["content"],
                    "status": "published",
                    "category": category,
                    "cover_image": ContentFile(
                        create_cover(data["art"], data["colors"]),
                        name=f'{data["slug"]}.png',
                    ),
                },
            )
            if not created:
                continue

            post.tags.set(
                [Tag.objects.get_or_create(name=name)[0] for name in data["tags"]]
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} of {len(POSTS)} sample posts "
                f"for {username}; existing posts were left unchanged."
            )
        )

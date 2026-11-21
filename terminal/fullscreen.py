import math
import random
import shutil
import sys
import time

RAIN = "我爱你永远星光心动梦想"
DURATION = 7
FPS = 15
ESC = "\033["

def inside(x, y, angle):
    front = abs(math.cos(angle))
    side = math.sin(angle)

    def oval(cx, cy, rx, ry):
        return ((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1

    # Broad capybara head, narrowing as it turns
    w = .34 + .20*front
    head = oval(side*.10, -.13, w, .39)
    muzzle = oval(side*.22, .09, .30, .20)

    ears = (
        oval(-w*.73, -.46, .115, .16) or
        oval(w*.73, -.46, .115, .16)
    )

    body = oval(0, .47, .46, .28)

    feet = (
        oval(-.29, .73, .12, .11) or
        oval(.29, .73, .12, .11)
    )

    return head or muzzle or ears or body or feet

def main():
    if not sys.stdout.isatty():
        return

    start = time.monotonic()
    drops = {}
    sys.stdout.write("\033[?25l")

    try:
        while True:
            elapsed = time.monotonic()-start
            if elapsed >= DURATION:
                break

            cols, rows = shutil.get_terminal_size((80,24))
            cols = max(12, cols)
            rows = max(6, rows)

            # Chinese characters occupy two terminal columns.
            cw = max(1, cols//2)
            h = max(1, rows-1)

            # Reinitialize rain when terminal is resized
            if len(drops) != cw:
                drops = {
                    x: random.randrange(-h, h)
                    for x in range(cw)
                }

            grid = [["  " for _ in range(cw)] for _ in range(h)]
            colors = [[0 for _ in range(cw)] for _ in range(h)]

            # Full-screen Chinese rain
            for x in range(cw):
                y = drops[x]
                for trail in range(7):
                    yy = y-trail
                    if 0 <= yy < h:
                        grid[yy][x] = random.choice(RAIN)
                        colors[yy][x] = [
                            117, 81, 45, 39, 33, 24, 17
                        ][trail]

                drops[x] += random.choice([1,1,2])
                if drops[x] >= h+7:
                    drops[x] = random.randrange(-h, 0)

            # Large central capybara
            cap_w = max(5, int(cw*.74))
            cap_h = max(4, int(h*.82))

            left = (cw-cap_w)//2
            top = (h-cap_h)//2

            angle = 2*math.pi*(elapsed/DURATION)

            for iy in range(cap_h):
                for ix in range(cap_w):
                    x = 2*ix/max(1,cap_w-1)-1
                    y = 2*iy/max(1,cap_h-1)-1

                    if inside(x,y,angle):
                        gx = left+ix
                        gy = top+iy

                        if 0 <= gx < cw and 0 <= gy < h:
                            grid[gy][gx] = RAIN[
                                (ix*5+iy*3)%len(RAIN)
                            ]

                            glow = (
                                math.sin(ix*.35+elapsed*5)+1
                            )/2
                            colors[gy][gx] = (
                                159 if glow>.75 else
                                117 if glow>.45 else 81
                            )

            # Build one frame to reduce flickering
            output = ["\033[H"]
            for y in range(h):
                current = None
                for x in range(cw):
                    color = colors[y][x]
                    if color != current:
                        output.append(
                            f"\033[38;5;{color}m"
                        )
                        current = color
                    output.append(grid[y][x])
                output.append("\033[0m")
                if y < h-1:
                    output.append("\n")

            sys.stdout.write("".join(output))
            sys.stdout.flush()
            time.sleep(1/FPS)

    finally:
        sys.stdout.write(
            "\033[0m\033[?25h\033[H\033[2J"
        )
        sys.stdout.flush()

if __name__ == "__main__":
    main()

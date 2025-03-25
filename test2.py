import pygame
import random
import os
import sys

# Khởi tạo pygame
pygame.init()

# Cài đặt màn hình
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooting Game")

# Màu sắc
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Đồng hồ game
clock = pygame.time.Clock()

# Đường dẫn ảnh cho người chơi (đảm bảo file ảnh nằm trong thư mục assets)
PLAYER_IMG_PATH = os.path.join("assets", "photo_2024-06-21_01-17-42.jpg")

# Class người chơi với ảnh và hiệu ứng nhấp nháy
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.original_image = pygame.image.load(PLAYER_IMG_PATH).convert_alpha()
        except Exception as e:
            print("Lỗi tải ảnh player:", e)
            self.original_image = pygame.Surface((80, 80))
            self.original_image.fill(BLUE)
        self.image = pygame.transform.scale(self.original_image, (80, 80))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.blink = False
        self.blink_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += 5

        # Hiệu ứng nhấp nháy: mỗi 500ms đổi trạng thái
        self.blink_timer += clock.get_time()
        if self.blink_timer >= 500:
            self.blink = not self.blink
            self.blink_timer = 0

        if self.blink:
            self.image.set_alpha(128)
        else:
            self.image.set_alpha(255)

# Class đạn
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 20))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= 10
        if self.rect.bottom < 0:
            self.kill()

# Class kẻ địch với ảnh từ folder "enemy"
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        enemy_folder = "enemy"
        enemy_images = [os.path.join(enemy_folder, f) for f in os.listdir(enemy_folder)
                        if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if enemy_images:
            chosen_image = random.choice(enemy_images)
            try:
                self.original_image = pygame.image.load(chosen_image).convert_alpha()
            except Exception as e:
                print("Lỗi tải ảnh enemy:", e)
                self.original_image = pygame.Surface((80, 80))
                self.original_image.fill(RED)
            self.original_image = pygame.transform.scale(self.original_image, (80, 80))
            self.image = self.original_image.copy()
        else:
            self.image = pygame.Surface((80, 80))
            self.image.fill(RED)
            self.original_image = self.image.copy()
        self.rect = self.image.get_rect(center=(random.randint(40, WIDTH - 40), 0))
        self.angle = 0

    def update(self):
        self.angle = (self.angle + 3) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.y += 3
        if self.rect.top > HEIGHT:
            self.kill()

# Class hiệu ứng nổ (không dùng ảnh), dùng hình tròn mở rộng
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, color=YELLOW, max_radius=50, duration=500):
        super().__init__()
        self.center = center
        self.color = color
        self.max_radius = max_radius
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.image = pygame.Surface((max_radius*2, max_radius*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        if elapsed >= self.duration:
            self.kill()
            return
        progress = elapsed / self.duration
        radius = int(self.max_radius * progress)
        alpha = int(255 * (1 - progress))
        self.image.fill((0, 0, 0, 0))
        if radius > 0:
            pygame.draw.circle(self.image, self.color + (alpha,), (self.max_radius, self.max_radius), radius)

# Class vật phẩm (Item) đơn giản: hiển thị dưới dạng hình tròn màu xanh
class Item(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.radius = 15
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(random.randint(20, WIDTH-20), 0))
        self.speed = random.randint(2, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Class địa hình (Terrain) đơn giản: hình chữ nhật màu xám
class Terrain(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = random.randint(100, 300)
        self.height = 30
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((100, 100, 100))  # Màu xám
        # Vị trí ngẫu nhiên trên chiều ngang, bắt đầu từ trên cùng
        x = random.randint(0, WIDTH - self.width)
        self.rect = self.image.get_rect(topleft=(x, -self.height))
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Tạo nhóm sprite
player = Player()
player_group = pygame.sprite.GroupSingle(player)
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
terrain_group = pygame.sprite.Group()

def spawn_enemy():
    if random.randint(1, 50) == 1:
        enemy_group.add(Enemy())

def spawn_item():
    if random.randint(1, 100) == 1:
        item_group.add(Item())

def spawn_terrain():
    # Spawn terrain thường xuyên hơn (ví dụ, mỗi 2 giây)
    if random.randint(1, 60) == 1:
        terrain_group.add(Terrain())

# Vòng lặp chính
running = True
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet_group.add(Bullet(player.rect.centerx, player.rect.top))
    
    # Cập nhật các sprite
    player_group.update()
    bullet_group.update()
    enemy_group.update()
    explosion_group.update()
    item_group.update()
    terrain_group.update()

    spawn_enemy()
    spawn_item()
    spawn_terrain()

    # Kiểm tra va chạm giữa đạn và kẻ địch, tạo hiệu ứng nổ
    for bullet in bullet_group:
        enemies_hit = pygame.sprite.spritecollide(bullet, enemy_group, True)
        if enemies_hit:
            for enemy in enemies_hit:
                explosion_group.add(Explosion(enemy.rect.center))
            bullet.kill()
    
    # Kiểm tra va chạm giữa người chơi và vật phẩm (item)
    items_collected = pygame.sprite.spritecollide(player, item_group, True)
    for item in items_collected:
        print("Item collected!")

    # Kiểm tra va chạm giữa người chơi và địa hình (terrain) -> Game over
    if pygame.sprite.spritecollide(player, terrain_group, False):
        print("Player hit terrain! Game Over!")
        running = False

    # Vẽ màn hình
    screen.fill((0, 0, 0))
    player_group.draw(screen)
    bullet_group.draw(screen)
    enemy_group.draw(screen)
    explosion_group.draw(screen)
    item_group.draw(screen)
    terrain_group.draw(screen)
    pygame.display.flip()
    
pygame.quit()

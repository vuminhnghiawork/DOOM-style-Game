import pygame
import random
import os

# Khởi tạo pygame
pygame.init()

# Cài đặt màn hình
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooting Game")

# Màu sắc
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Đồng hồ game
clock = pygame.time.Clock()

# Đường dẫn ảnh cho người chơi (đảm bảo file ảnh nằm trong thư mục assets)
PLAYER_IMG_PATH = os.path.join("assets", "photo_2024-06-21_01-17-42.jpg")

# Tạo class cho người chơi với ảnh và hiệu ứng nhấp nháy
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load(PLAYER_IMG_PATH).convert_alpha()
        # Tùy chỉnh kích thước ảnh (50x50)
        self.image = pygame.transform.scale(self.original_image, (50, 50))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        # Khởi tạo biến hiệu ứng nhấp nháy
        self.blink = False
        self.blink_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += 5

        # Cập nhật hiệu ứng nhấp nháy: mỗi 500ms thay đổi trạng thái
        self.blink_timer += clock.get_time()
        if self.blink_timer >= 500:
            self.blink = not self.blink
            self.blink_timer = 0

        # Áp dụng hiệu ứng: giảm độ trong suốt khi blink
        if self.blink:
            self.image.set_alpha(128)  # 50% trong suốt
        else:
            self.image.set_alpha(255)

# Tạo class cho đạn
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

# Tạo class cho kẻ thù sử dụng ảnh từ folder "enemy"
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        enemy_folder = "enemy"  # Folder chứa ảnh của kẻ địch
        # Lấy danh sách các file ảnh từ folder (hỗ trợ png, jpg, jpeg)
        enemy_images = [os.path.join(enemy_folder, f) for f in os.listdir(enemy_folder)
                        if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if enemy_images:
            # Chọn ngẫu nhiên một ảnh
            chosen_image = random.choice(enemy_images)
            self.image = pygame.image.load(chosen_image).convert_alpha()
            # Tùy chỉnh kích thước ảnh (40x40)
            self.image = pygame.transform.scale(self.image, (40, 40))
        else:
            # Nếu không có ảnh nào, sử dụng hình chữ nhật màu đỏ
            self.image = pygame.Surface((40, 40))
            self.image.fill(RED)
        self.rect = self.image.get_rect(center=(random.randint(20, WIDTH - 20), 0))

    def update(self):
        self.rect.y += 3
        if self.rect.top > HEIGHT:
            self.kill()

# Tạo nhóm sprite
player = Player()
player_group = pygame.sprite.GroupSingle(player)
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

def spawn_enemy():
    if random.randint(1, 50) == 1:
        enemy_group.add(Enemy())

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
    spawn_enemy()

    # Kiểm tra va chạm giữa đạn và kẻ thù
    for bullet in bullet_group:
        enemies_hit = pygame.sprite.spritecollide(bullet, enemy_group, True)
        if enemies_hit:
            bullet.kill()
    
    # Vẽ các sprite lên màn hình
    screen.fill((0, 0, 0))
    player_group.draw(screen)
    bullet_group.draw(screen)
    enemy_group.draw(screen)
    pygame.display.flip()
    
pygame.quit()


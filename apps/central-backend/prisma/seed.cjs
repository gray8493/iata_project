const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcrypt');

const prisma = new PrismaClient();

async function main() {
  console.log('--- Bắt đầu khởi tạo dữ liệu mẫu cho Neon Postgres ---');

  // 1. Tạo tài khoản Admin
  const adminUsername = process.env.BOOTSTRAP_ADMIN_USERNAME || 'admin';
  const adminPassword = process.env.BOOTSTRAP_ADMIN_PASSWORD || 'Admin@123456';
  const adminFullName = process.env.BOOTSTRAP_ADMIN_FULL_NAME || 'Quản Trị Viên AITA';
  const adminEmail = process.env.BOOTSTRAP_ADMIN_EMAIL || 'admin@aita.edu.vn';

  let adminUser = await prisma.user.findFirst({
    where: { username: adminUsername, isDeleted: false },
  });

  if (!adminUser) {
    const passwordHash = await bcrypt.hash(adminPassword, 12);
    adminUser = await prisma.user.create({
      data: {
        username: adminUsername,
        passwordHash,
        fullName: adminFullName,
        email: adminEmail,
        role: 'ADMIN',
        isActive: true,
      },
    });
    console.log(`✓ Đã tạo Admin: ${adminUsername} (Mật khẩu: ${adminPassword})`);
  } else {
    console.log(`- Admin [${adminUsername}] đã tồn tại.`);
  }

  // Quota AI cho Admin (100.000 tokens)
  await prisma.aiQuotaConfig.upsert({
    where: { userId: adminUser.id },
    create: {
      userId: adminUser.id,
      dailyTokenLimit: 100000,
      usedTokensToday: 0,
    },
    update: {},
  });

  // 2. Tạo tài khoản Giảng viên (Instructor)
  const instructorUsername = process.env.BOOTSTRAP_INSTRUCTOR_USERNAME || 'instructor';
  const instructorPassword = process.env.BOOTSTRAP_INSTRUCTOR_PASSWORD || 'Instructor@123456';
  const instructorFullName = process.env.BOOTSTRAP_INSTRUCTOR_FULL_NAME || 'Thầy Nguyễn Văn An';
  const instructorEmail = process.env.BOOTSTRAP_INSTRUCTOR_EMAIL || 'instructor@aita.edu.vn';

  let instructorUser = await prisma.user.findFirst({
    where: { username: instructorUsername, isDeleted: false },
  });

  if (!instructorUser) {
    const passwordHash = await bcrypt.hash(instructorPassword, 12);
    instructorUser = await prisma.user.create({
      data: {
        username: instructorUsername,
        passwordHash,
        fullName: instructorFullName,
        email: instructorEmail,
        role: 'INSTRUCTOR',
        isActive: true,
      },
    });
    console.log(`✓ Đã tạo Instructor: ${instructorUsername} (Mật khẩu: ${instructorPassword})`);
  } else {
    console.log(`- Instructor [${instructorUsername}] đã tồn tại.`);
  }

  // Quota AI cho Instructor (50.000 tokens)
  await prisma.aiQuotaConfig.upsert({
    where: { userId: instructorUser.id },
    create: {
      userId: instructorUser.id,
      dailyTokenLimit: 50000,
      usedTokensToday: 0,
    },
    update: {},
  });

  console.log('--- Hoàn thành khởi tạo dữ liệu trên Neon Postgres! ---');
}

main()
  .catch((error) => {
    console.error('Lỗi khởi tạo dữ liệu:', error);
    process.exitCode = 1;
  })
  .finally(async () => {
    await prisma.$disconnect();
  });

/*YTD*/

/*Headline Tag - New Accounts (Phần trăm hoàn thành chỉ tiêu tháng - Tài khoản mở mới) */

BEGIN


DECLARE @Date DATETIME;
SET @Date = @YYYYMMDD;

DECLARE @FirstDateOfCurrentYear DATETIME;
SET @FirstDateOfCurrentYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date),1,1,0,0,0,0));

DECLARE @DateOfPreviousYear DATETIME;
IF MONTH(@Date) = 2 AND DAY(@Date) = 29
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,2,28,0,0,0,0));
ELSE
	SET @DateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@Date)-1,MONTH(@Date),DAY(@Date),0,0,0,0));

DECLARE @FirstDateOfPreviousYear DATETIME;
SET @FirstDateOfPreviousYear = (SELECT DATETIMEFROMPARTS(YEAR(@DateOfPreviousYear),1,1,0,0,0,0));

WITH

[TargetByBranch] AS (
	SELECT
		[BranchID]
	FROM [BranchTargetByYear]
	WHERE [Year] = YEAR(@Date)
		AND [Measure] = 'New Accounts'
)

, [RRE0386.Flex] AS (
	SELECT
		[AUTOID]
		, MIN([AUTOID]) OVER (PARTITION BY [SoTaiKhoan], [NgayMoTK]) [MinID]
		, [NgayMoTK]
		, [SoTaiKhoan]
		, [IDNhanVienMoTK]
	FROM [RRE0386]
	WHERE (
		([RRE0386].[NgayMoTK] BETWEEN @FirstDateOfPreviousYear AND @DateOfPreviousYear)
		OR ([RRE0386].[NgayMoTK] BETWEEN @FirstDateOfCurrentYear AND @Date)
	)
	AND [RRE0386].[IDNhanVienHienTai] IS NOT NULL
)

, [FindLastBranchID] AS (
	SELECT DISTINCT
		[relationship].[date]
		, [relationship].[account_code] [SoTaiKhoan]
		, [broker_id]
		, LAST_VALUE([branch_id]) OVER(PARTITION BY [account_code], [broker_id] ORDER BY [account_code]) [branch_id]
	FROM [relationship]
	WHERE (
		([date] BETWEEN @FirstDateOfPreviousYear AND @DateOfPreviousYear)
		OR ([date] BETWEEN @FirstDateOfCurrentYear AND @Date)
	)
	AND [relationship].[account_code] IN (SELECT [SoTaiKhoan] FROM [RRE0386.Flex])
)

, [Rel] AS (
	SELECT
		[Date]
		, [SoTaiKhoan]
		, CASE
			WHEN [broker_id] IS NULL AND [date] <> @Date THEN LEAD([branch_id]) OVER (PARTITION BY [SoTaiKhoan] ORDER BY [date])
			ELSE [branch_id]
		END [BranchID]
	FROM [FindLastBranchID]
)

, [_RRE0386] AS (
	SELECT
		[NgayMoTK]
		, [SoTaiKhoan]
		, [IDNhanVienMoTK]
	FROM [RRE0386.Flex]
	WHERE [MinID] = [AUTOID]
)

, [ValueByPrevPeriod] AS (
	SELECT
		COUNT(*) [NewAccounts]
	FROM [_RRE0386]
	LEFT JOIN [Rel]
		ON [Rel].[SoTaiKhoan] = [_RRE0386].[SoTaiKhoan]
		AND [Rel].[Date] = [_RRE0386].[NgayMoTK]
	WHERE [Rel].[BranchID] IN (SELECT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@DateOfPreviousYear) AND [Measure] = 'New Accounts')
		AND [date] BETWEEN @FirstDateOfPreviousYear AND @DateOfPreviousYear
)

, [ValueCurrentPeriod] AS (
	SELECT
		COUNT(*) [NewAccounts]
	FROM [_RRE0386]
	LEFT JOIN [Rel]
		ON [Rel].[SoTaiKhoan] = [_RRE0386].[SoTaiKhoan]
		AND [Rel].[Date] = [_RRE0386].[NgayMoTK]
	WHERE [Rel].[BranchID] IN (SELECT [BranchID] FROM [BranchTargetByYear] WHERE [Year] = YEAR(@Date) AND [Measure] = 'New Accounts')
		AND [date] BETWEEN @FirstDateOfCurrentYear AND @Date
)

SELECT
	[ValueCurrentPeriod].[NewAccounts] [NewAccounts]
	, CAST([ValueCurrentPeriod].[NewAccounts] AS DECIMAL(10,5)) - CAST([ValueByPrevPeriod].[NewAccounts] AS DECIMAL(10,5)) [AbsoluteChange]
	, CASE [ValueByPrevPeriod].[NewAccounts]
		WHEN 0 THEN 0
		ELSE CAST([ValueCurrentPeriod].[NewAccounts] AS DECIMAL(10,5)) / CAST([ValueByPrevPeriod].[NewAccounts] AS DECIMAL(10,5)) - 1
	END [RelativeChange]
FROM [ValueByPrevPeriod]
CROSS JOIN [ValueCurrentPeriod]


END
